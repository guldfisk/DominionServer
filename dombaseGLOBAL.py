import random
from pydispatch import dispatcher as dp
import re
import numpy as np
import math as m
import pprint
import copy

class CPile(list):
	def __init__(self, *args, **kwargs):
		super(CPile, self).__init__(*args)
		self.faceup = kwargs.get('faceup', True)
		self.name = kwargs.get('name', True)
	def getFullView(self):
		ud = ''
		for i in range(len(self)-1, -1, -1):
			ud += self[i].view() + ', '
		return ud[:-1]
	def getView(self):
		if self.faceup: return self.getFullView()
		else: return str(len(self))+' cards'
	def popx(self, pos=None):
		if self:
			if not pos==None: return self.pop(pos)
			else: return self.pop()
		else: return None
	def viewTop(self):
		if not self: return None
		return self[-1]

allCards = []
delayedActions = []
trash = CPile()
players = []
piles = {}
activePlayer = None
globalMats = {}
emptyPiles = []
emptyTerminatorPiles = 0
events = []
turnFlag = ''

def getNextPlayer(cplayer):
	if not len(players)>1: return cplayer
	for i in range(len(players)):
		if players[i]==cplayer: return players[(i+1)%len(players)]

def getPreviousPlayer(cplayer):
	if not len(players)>1: return cplayer
	for i in range(len(players)):
		if players[i]==cplayer: return players[i-1]
		
def getPlayers(cplayer):
	for i in range(len(players)):
		if players[i]==cplayer:
			yield cplayer
			n=(i+1)%len(players)
			while players[n]!=cplayer:
				yield players[n]
				n=(n+1)%len(players)
				
def addGlobalMat(name):
	globalMats[name] = []

def addMat(name):
	for player in players: player.mats[name] = []
	
def checkGameEnd(piles):
	emptyPiles = 0
	for pile in piles:
		if not piles[pile].pile:
			if piles[pile].terminator:
				return True
			emptyPiles += 1
	if emptyPiles>=3: return True
	return False

def gN(ob):
	if hasattr(ob, 'playerName'): return ob.playerName
	elif hasattr(ob, 'name'): return ob.name
	else: return str(ob)
	
def testUser(options):
	for option in options: print(gN(option), end=', ')
	choicePosition = -2
	while choicePosition<-1:
		choice = input(': ')
		if not choice: return len(options)-1
		for i in range(len(options)):
			if re.match(choice, gN(options[i]), re.IGNORECASE):
				choicePosition = i
				break
	return choicePosition
	
def makeStartDeck():
	for player in players:
		for i in range(7):
			player.gainFromPile(piles['Copper'])
		for i in range(3):
			player.gainFromPile(piles['Estate'])

def evLogger(signal, **kwargs):
	events.append((signal, kwargs))
			
def game(endCondition=checkGameEnd):
	round = 0
	dp.connect(evLogger)
	dp.send(signal='globalSetup', players=players)
	while delayedActions: delayedActions.pop()()
	for player in players:
		player.setup()
	while True:
		round+=1
		dp.send(signal='beginRound', round=round)
		for player in players:
			player.takeTurn()
			if endCondition(piles):
				for player in players:
					player.endGame()
				players.sort(key=lambda x: x.victories, reverse=True)
				points = {}
				for player in players:
					while delayedActions: delayedActions.pop()()
					points[player] = player.victories
				dp.send(signal='gameEnd', winner=players[0], points=points)
				return
			
class Game:
	def __init__(self, **kwargs):
		self.allCards = []
		self.delayedActions = []
		self.trash = CPile()
		self.players = []
		self.piles = {}
		self.activePlayer = None
		self.globalMats = {}
		self.emptyPiles = []
		self.emptyTerminatorPiles = 0
		self.events = []
		self.turnFlag = ''
		
class Player:
	def __init__(self, **kwargs):
		self.coins = 0
		self.potions = 0
		self.actions = 0
		self.buys = 0
		self.victories = 0
		self.hand = CPile(name='hand', faceup=False)
		self.library = CPile(name='library', faceup=False)
		self.inPlay = CPile(name='inPlay')
		self.discardPile = CPile(name='discardPile')
		self.mats = {}
		self.user = testUser
		self.playerName = kwargs.get('name', 'p1')
		self.channelOut = None
		dp.connect(self.toPlayer)
		players.append(self)
	def request(self, head):
		print('HEAD', head)
		if head=='stat': return 'Actions: '+str(self.actions)+'\tCoins: '+str(self.coins)+'\tBuys: '+str(self.buys)
		elif head=='king':
			ud = ''
			for key in sorted(piles): ud+=key+': '+str(len(piles[key].pile))+', '
			return ud
	def toPlayer(self, signal, **kwargs):
		if not self.channelOut: return
		if signal=='tryBuy': return
		s = [signal, {}]
		hidden = False
		censored = ['card']
		if 'hidden' in kwargs: hidden = kwargs['hidden']
		if 'censored' in kwargs: censored = kwargs['censored']
		for key in kwargs: 
			if not (key=='sender' or key=='hidden' or key=='kwargs' or (hidden and hidden!=self and key in censored)):
				s[1][key] = gN(kwargs[key])
		self.channelOut(s)
	def getView(self):
		return 'Hand: '+self.hand.getFullView()+'\nIn Play: '+self.inPlay.getView()+'\nDiscard: '+self.discardPile.getView()+'\nLibrary: '+self.library.getView()+'\nCoins: '+str(self.coins)+'\tActions: '+str(self.actions)+'\tBuys: '+str(self.buys)
	def view(self):
		print(self.getView())
	def setup(self, **kwargs):
		dp.send(signal='setup', player=self)
		self.reshuffle()
		self.draw(amnt=5)
	def takeTurn(self, **kwargs):
		global activePlayer
		global turnFlag
		activePlayer = self
		turnFlag = ''
		self.resetValues()
		dp.send(signal='startTurn', player=self)
		self.actionPhase()
		self.treasurePhase()
		self.buyPhase()
		self.endTurn()
	def actionPhase(self, **kwargs):
		dp.send(signal='actionPhase', player=self)
		while True:
			self.channelOut(self.request('stat'), 'resp', False)
			if self.actions<1 or not self.hand: break
			choice = self.user([o.name for o in self.hand]+['EndActionPhase'], 'Choose action')
			if choice+1>len(self.hand): break
			print(self.hand[choice].types)
			if not 'ACTION' in self.hand[choice].types: continue
			self.actions-=1
			playedAction = self.hand.pop(choice)
			self.inPlay.append(playedAction)
			self.playAction(playedAction)
	def treasurePhase(self, **kwargs):
		dp.send(signal='treasurePhase', player=self)
		while True:
			self.channelOut(self.request('stat'), 'resp', False)
			if not self.hand: break
			choice = self.user([o.name for o in self.hand]+['PlayAllTreasures', 'EndTreasurePhase'], 'Choose treasure')
			if choice>len(self.hand): break
			if choice==len(self.hand):
				for i in range(len(self.hand)-1, -1, -1):
					if not 'TREASURE' in self.hand[i].types: continue
					playedTreasure = self.hand.pop(i)
					self.inPlay.append(playedTreasure)
					self.playTreasure(playedTreasure)
				break
			elif 'TREASURE' in self.hand[choice].types:
				playedTreasure = self.hand.pop(choice)
				self.inPlay.append(playedTreasure)
				self.playTreasure(playedTreasure)
	def buyPhase(self, **kwargs):
		dp.send(signal='buyPhase', player=self)
		self.channelOut(self.request('king'), 'resp', False)
		while self.buys>0:
			self.channelOut(self.request('stat'), 'resp', False)
			choice = self.user(list(piles)+['EndBuyPhase'], 'buySelection')
			if choice+1>len(piles): break
			self.buy(piles[list(piles)[choice]])
	def getFromPlay(self, position=None):
		if position==None:
			self.inPlay[-1].onLeavePlay(self)
			return self.inPlay.pop()
		else:
			self.inPlay[position].onLeavePlay(self)
			return self.inPlay.pop(position)
	def destroyCard(self, card, **kwargs):
		if not card.onDestroy(self) and not dp.send(signal='destroy', player=self, card=card):
			card.onLeavePlay(self)
			self.discardPile.append(card)
	def destroyAll(self, **kwargs):
		print('STARTDESTROYALL', [o.name for o in self.inPlay], self.inPlay)
		for card in copy.copy(self.inPlay):
			print(card, card.name)
			if not card.onDestroy(self) and not dp.send(signal='destroy', player=self, card=card):
				for i in range(len(self.inPlay)):
					print('\t', self.inPlay[i])
					if card==self.inPlay[i]:
						card.onLeavePlay(self)
						self.discardPile.append(self.inPlay.pop(i))
						break
		print('ENDDESTROYALL', [o.name for o in self.inPlay], len(self.inPlay))
	def getCard(self, **kwargs):
		if not self.library:
			self.reshuffle()
			if not self.library: return 'Empty'
		return self.library.pop()
	def getCards(self, amnt=1, **kwargs):
		cards = []
		for i in range(amnt):
			drawnCard = self.getCard()
			if drawnCard=='Empty': break
			cards.append(drawnCard)
		return cards
	def draw(self, **kwargs):
		for i in range(kwargs.get('amnt', 1)):
			drawnCard = self.getCard()
			if drawnCard=='Empty': return drawnCard
			dp.send(signal='draw', player=self, card=drawnCard, hidden=self)
			self.hand.append(drawnCard)
	def reshuffle(self, **kwargs):
		dp.send(signal='shuffle', player=self)
		while self.discardPile:
			self.library.append(self.discardPile.pop())
		random.shuffle(self.library)
	def trash(self, position = 0, **kwargs):
		trashedCard = kwargs.get('xfrom', self.hand).pop(position)
		self.trashCard(trashedCard, **kwargs)
	def trashCard(self, card, **kwargs):
		if not card.onTrash(self) and not dp.send(signal='trash', player=self, card=card):
			card.owner = None
			trash.append(card)
	def returnCard(self, card, **kwargs):
		if not card.name in piles: return
		dp.send(signal='return', player=self, card=card)
		piles[card.name].pile.append(card)
	def discard(self, position = 0, **kwargs):
		discardedCard = self.hand.pop(position)
		self.discardCard(discardedCard, **kwargs)
	def discardCard(self, card, **kwargs):
		if not card.onDiscard(self) and not dp.send(signal='discard', player=self, card=card): self.discardPile.append(card)
	def revealPosition(self, position = 0, **kwargs):
		if kwargs.get('fromZ', self.hand)==self.library and not self.library:
			self.reshuffle()
			if not self.library: return
		if not kwargs.get('fromZ', self.hand): return
		dp.send(signal='reveal', player=self, card=kwargs.get('fromZ', self.hand)[position], position=position, fromZ=kwargs.get('fromZ', self.hand).name)
		return kwargs.get('fromZ', self.hand)[position]
	def reveal(self, card, **kwargs):
		dp.send(signal='reveal', player=self, card=card, fromZ=kwargs.get('fromZ', self.hand).name, **kwargs)
	def discardHand(self, **kwargs):
		while self.hand:
			self.discard()
	def resetValues(self, **kwargs):
		self.coins = 0
		self.potions = 0
		self.actions = 1
		self.buys = 1
	def endTurn(self, **kwargs):
		dp.send(signal='endTurn', player=self)
		self.discardHand()
		self.destroyAll()
		self.draw(amnt=5)
		self.resetValues()
		dp.send(signal='turnEnded', player=self)
	def endGame(self, **kwargs):
		self.discardHand()
		self.destroyAll()
		for key in self.mats:
			for i in range(len(self.mats[key])-1, -1, -1):
				if isinstance(self.mats[key][i], Card): self.library.append(self.mats[key].pop(i))
		self.reshuffle()
		for card in self.library:
			card.onGameEnd(self)
	def give(self, card, **kwargs):
		self.discardPile.append(card)
		card.owner = self
	def take(self, pile, **kwargs):
		dp.send(signal='take', player=self, pile=pile)
		cardGained = pile.gain()
		cardGained.owner = self
		cardGained.onGain(self)
		self.discardPile.append(cardGained)
	def gain(self, card, **kwargs):
		if card and not card.onGain(self) and not dp.send(signal='gain', player=self, card=card, fromz=kwargs.get('fromz', None), kwargs=kwargs):
			card.owner = self
			kwargs.get('to', self.discardPile).append(card)
	def gainFromPile(self, pile, **kwargs):
		self.gain(pile.gain(), fromz=pile, **kwargs)
	def buy(self, pile, **kwargs):
		if pile.pile and self.buys>0 and pile.pile[-1].getPrice(self)<=self.coins and pile.pile[-1].getPotionPrice(self)<=self.potions and not dp.send(signal='tryBuy', player=self, pile=pile, card=pile.pile.viewTop()):
			dp.send(signal='buy', player=self, pile=pile, card=pile.pile.viewTop())
			self.buys -= 1
			self.coins -= pile.pile[-1].getPrice(self)
			self.potions -= pile.pile[-1].getPotionPrice(self)
			self.gain(pile.gain(), fromz=pile)
	def playAction(self, card, **kwargs):
		dp.send(signal='playAction', player=self, card=card)
		card.onPlay(self)
	def playTreasure(self, card, **kwargs):
		dp.send(signal='playTreasure', player=self, card=card)
		card.onPlay(self)
	def attack(self, attack, source, **kwargs):
		if dp.send(signal='attack', player=self, card=source, attack=attack, **kwargs): return
		attack(self, **kwargs)
	def addCoin(self, **kwargs):
		dp.send(signal='addCoin', player=self, amnt=kwargs.get('amnt', 1))
		self.coins += kwargs.get('amnt', 1)
	def addBuy(self, **kwargs):
		dp.send(signal='addBuy', player=self, amnt=kwargs.get('amnt', 1))
		self.buys += kwargs.get('amnt', 1)
	def addAction(self, **kwargs):
		dp.send(signal='addAction', player=self, amnt=kwargs.get('amnt', 1))
		self.actions += kwargs.get('amnt', 1)
	def addVictory(self, **kwargs):
		dp.send(signal='addVictory', player=self, amnt=kwargs.get('amnt', 1))
		self.victories += kwargs.get('amnt', 1)
	
class Token:
	name = 'baseToken'
	def __init__(self, **kwargs):
		self.owner = kwargs.get('owner', None)
	
class Pile:
	def __init__(self, cardType, **kwargs):
		self.cardType = cardType
		self.pile = CPile()
		self.terminator = kwargs.get('terminator', False)
		self.cardType().onPileCreate(self) #X fucking D
		self.name = self.cardType().name
		self.tokens = []
		for card in self.pile:
			allCards.append(card)
	def gain(self, **kwargs):
		if not self.pile: return
		popped = self.pile.pop()
		if not self.pile:
			emptyPiles.append(self)
			if self.terminator:
				global emptyTerminatorPiles
				emptyTerminatorPiles += 1
		print('EMPTY', emptyPiles)
		return popped
	def getView(self):
		return self.name+': '+str(len(self.pile))
	def addToken(self, token, **kwargs):
		dp.send(signal='addTokenPile', pile=self, token=token)
		token.owner = self
		self.tokens.append(token)
	def removeToken(self, token, **kwargs):
		dp.send(signal='removeTokenPile', pile=self, token=token)
		token.owner = None
		
def makePiles(cards):
	for card in cards:
		piles[card.name] = Pile(card)
		
def getPilesView():
	ud = ''
	for pile in piles: ud+=piles[pile].getView()+', '
	return ud
	
class CardAdd:
	def onPileCreate(self, pile, **kwargs):
		for i in range(10):
			pile.pile.append(type(self)())
	def getPrice(self, player, **kwargs):
		return np.max((self.price, 0))
	def getPotionPrice(self, player, **kwargs):
		return np.max((self.potionPrice, 0))
	def view(self, **kwargs):
		return self.name
	def onPlay(self, player, **kwargs):
		pass
	def onDestroy(self, player, **kwargs):
		pass
	def onGain(self, player, **kwargs):
		pass
	def onTrash(self, player, **kwargs):
		pass
	def onGameEnd(self, player, **kwargs):
		pass
	def onReturn(self, player, **kwargs):
		pass
	def onDiscard(self, player, **kwargs):
		pass
	def onLeavePlay(self, player, **kwargs):
		pass
	
class Card:
	name = 'BaseCard'
	def __init__(self, **kwargs):
		if not hasattr(self, 'types'): self.types = []
		self.price = kwargs.get('price', 0)
		self.potionPrice = kwargs.get('potionPrice', 0)
		self.owner = None
		
class Treasure(Card):
	def __init__(self, **kwargs):
		super(Treasure, self).__init__(**kwargs)
		self.value = 1
		self.types.append('TREASURE')
	def onPlay(self, player, **kwargs):
		super(Treasure, self).onPlay(player, **kwargs)
		player.addCoin(amnt=self.value)
	def getValue(self, **kwargs):
		return np.max((self.value, 0))
		
class Victory(Card):
	def __init__(self, **kwargs):
		super(Victory, self).__init__(**kwargs)
		self.value = 1
		self.types.append('VICTORY')
	def onGameEnd(self, player, **kwargs):
		player.addVictory(amnt=self.value)
		
class Action(Card):
	def __init__(self, **kwargs):
		super(Action, self).__init__(**kwargs)
		self.types.append('ACTION')
		
class Cursed(Card):
	def __init__(self, **kwargs):
		super(Cursed, self).__init__(**kwargs)
		self.value = -1
		self.types.append('CURSED')
	def onGameEnd(self, player, **kwargs):
		player.addVictory(amnt=self.value)
		
class Reaction():
	def __init__(self, **kwargs):
		self.types.append('REACTION')
		self.signal = 'noSignal'
	def trigger(self, signal, **kwargs):
		pass
	def connect(self, **kwargs):
		dp.connect(self.trigger, signal=self.signal)
	def disconnect(self, **kwargs):
		dp.connect(self.trigger, signal=self.signal)
		
class Attack():
	def __init__(self, **kwargs):
		self.types.append('ATTACK')
		
class Duration():
	def __init__(self, **kwargs):
		self.types.append('Duration')
		self.age = 0
		self.nexts = []
	def onPlay(self, player, **kwargs):
		self.nexts.append(self.next)
		dp.connect(self.trigger, signal='startTurn')
		self.age = 0
	def onDestroy(self, player, **kwargs):
		if self.age<1: return True
	def onLeavePlay(self, player, **kwargs):
		dp.disconnect(self.trigger, signal='startTurn')
	def trigger(self, signal, **kwargs):
		if not kwargs['player']==self.owner: return
		self.age+=1
		print(self, self.nexts)
		while self.nexts: self.nexts.pop()()
	def next(self, **kwargs):
		pass
	
if __name__=='__main__':
	random.seed()