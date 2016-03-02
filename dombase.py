import random
from pydispatch import dispatcher as dp
import re
import numpy as np
import math as m
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

class Game(object):
	def __init__(self, **kwargs):
		self.allCards = []
		self.delayedActions = []
		self.trash = CPile(name='Trash')
		self.players = kwargs.get('players', [])
		self.piles = {}
		self.NSPiles = {}
		self.activePlayer = None
		self.globalMats = {}
		self.emptyPiles = []
		self.emptyTerminatorPiles = 0
		self.events = []
		self.turnFlag = ''
		self.round = 0
		self.dp = dp.Dispatcher()
	def require(self, card, **kwargs):
		if card.name in list(self.NSPiles): return
		self.NSPiles[card.name] = Pile(card, self)
	def evLogger(self, signal, **kwargs):
		self.events.append((signal, kwargs))
	def emptyDelayed(self):
		print('EMPTY DELAYED', len(self.delayedActions), self.delayedActions)
		while self.delayedActions:
			action = self.delayedActions.pop()
			action[0](**action[1])
	def start(self, endCon=None):
		if not endCon: endCondition = self.checkGameEnd
		else: endCondition = endCon
		self.round = 0
		self.dp.connect(self.evLogger)
		for player in self.players: self.dp.connect(player.toPlayer)
		self.dp.send(signal='globalSetup', players=self.players)
		self.emptyDelayed()
		for player in self.players: player.setup(self)
		while True:
			self.round+=1
			self.dp.send(signal='beginRound', round=self.round)
			for player in self.players:
				player.takeTurn()
				if endCondition():
					self.endGame()
					return
				self.emptyDelayed()
	def endGame(self):
		self.dp.send(signal='gameEnding')
		for player in self.players: player.endGame()
		self.players.sort(key=lambda x: x.victories, reverse=True)
		points = {}
		for player in self.players: points[player.name] = player.victories
		self.dp.send(signal='gameEnd', winner=self.players[0], points=points)
	def getNextPlayer(self, cplayer):
		if not cplayer in self.players: return
		if not len(self.players)>1: return cplayer
		for i in range(len(self.players)):
			if self.players[i]==cplayer: return self.players[(i+1)%len(players)]	
	def getPreviousPlayer(self, cplayer):
		if not cplayer in self.players: return
		if not len(self.players)>1: return cplayer
		for i in range(len(self.players)):
			if self.players[i]==cplayer: return self.players[i-1]
	def getPlayers(self, cplayer):
		for i in range(len(self.players)):
			if self.players[i]==cplayer:
				yield cplayer
				n=(i+1)%len(self.players)
				while self.players[n]!=cplayer:
					yield self.players[n]
					n=(n+1)%len(self.players)
	def addGlobalMat(self, name):
		if not name in list(self.globalMats): self.globalMats[name] = []
	def addMat(self, name):
		for player in self.players:
			if not name in list(player.mats): player.mats[name] = []
	def checkGameEnd(self):
		emptyPiles = 0
		for pile in self.piles:
			if not self.piles[pile]:
				if self.piles[pile].terminator:
					return True
				emptyPiles += 1
		if emptyPiles>=3: return True
		return False
	def makePiles(self, cards):
		for card in cards:
			self.piles[card.name] = Pile(card, self)
	def getPilesView(self):
		ud = ''
		for pile in self.piles: ud+=self.piles[pile].getView()+', '
		return ud
	def makeStartDeck(self):
		for player in self.players:
			for i in range(7): player.gainFromPile(self.piles['Copper'])
			for i in range(3): player.gainFromPile(self.piles['Estate'])
			#player.gainFromPile(self.piles['Page'])
			for card in player.discardPile: self.allCards.append(card)
	
class Player(object):
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
		self.name = kwargs.get('name', 'p1')
		self.channelOut = None
		self.game = None
		self.eotdraw = 5
		self.journey = True
	def flipJourney(self):
		self.journey = not self.journey
		return self.journey
	def request(self, head):
		print('HEAD', head)
		if head=='stat': return 'Actions: '+str(self.actions)+'\tCoins: '+str(self.coins)+'\tBuys: '+str(self.buys)
		elif head=='king':
			ud = ''
			for key in sorted(self.game.piles): ud+=key+' '+str(self.game.piles[key].maskot.getPrice(self))+'$: '+str(len(self.game.piles[key]))+', '
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
			if not (key=='sender' or key=='hidden' or key=='kwargs' or (hidden and hidden!=self and key in censored)): s[1][key] = gN(kwargs[key])
		if signal=='globalSetup': s[1]['you'] = self.name
		self.channelOut(s)
	def getView(self):
		return 'Hand: '+self.hand.getFullView()+'\nIn Play: '+self.inPlay.getView()+'\nDiscard: '+self.discardPile.getView()+'\nLibrary: '+self.library.getView()+'\nCoins: '+str(self.coins)+'\tActions: '+str(self.actions)+'\tBuys: '+str(self.buys)
	def view(self):
		print(self.getView())
	def setup(self, game, **kwargs):
		game.dp.send(signal='setup', player=self)
		self.game = game
		self.reshuffle()
		self.draw(amnt=5)
	def takeTurn(self, **kwargs):
		self.game.activePlayer = self
		self.game.turnFlag = ''
		self.resetValues()
		self.game.dp.send(signal='startTurn', player=self)
		self.actionPhase()
		self.treasurePhase()
		self.buyPhase()
		self.endTurn()
	def actionPhase(self, **kwargs):
		self.game.dp.send(signal='actionPhase', player=self)
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
		self.game.dp.send(signal='treasurePhase', player=self)
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
		self.game.dp.send(signal='buyPhase', player=self)
		self.channelOut(self.request('king'), 'resp', False)
		while self.buys>0:
			self.channelOut(self.request('stat'), 'resp', False)
			choice = self.user(list(self.game.piles)+['EndBuyPhase'], 'buySelection')
			if choice+1>len(self.game.piles): break
			self.buy(self.game.piles[list(self.game.piles)[choice]])
	def getFromPlay(self, position=None):
		if position==None:
			self.inPlay[-1].onLeavePlay(self)
			return self.inPlay.pop()
		else:
			self.inPlay[position].onLeavePlay(self)
			return self.inPlay.pop(position)
	def destroyCard(self, card, **kwargs):
		if not card.onDestroy(self) and not self.game.dp.send(signal='destroy', player=self, card=card):
			card.onLeavePlay(self)
			self.discardPile.append(card)
	def destroyAll(self, **kwargs):
		print('STARTDESTROYALL', [o.name for o in self.inPlay], self.inPlay)
		for card in copy.copy(self.inPlay):
			if not card.onDestroy(self) and not self.game.dp.send(signal='destroy', player=self, card=card):
				for i in range(len(self.inPlay)):
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
			self.game.dp.send(signal='draw', player=self, card=drawnCard, hidden=self)
			self.hand.append(drawnCard)
	def reshuffle(self, **kwargs):
		self.game.dp.send(signal='shuffle', player=self)
		while self.discardPile:
			self.library.append(self.discardPile.pop())
		random.shuffle(self.library)
	def trash(self, position = 0, **kwargs):
		trashedCard = kwargs.get('xfrom', self.hand).pop(position)
		self.trashCard(trashedCard, **kwargs)
	def trashCard(self, card, **kwargs):
		if not card.onTrash(self) and not self.game.dp.send(signal='trash', player=self, card=card):
			card.owner = None
			self.game.trash.append(card)
	def returnCard(self, card, **kwargs):
		if card.name in self.game.piles:
			self.game.dp.send(signal='return', player=self, card=card)
			self.game.piles[card.name].append(card)
		elif card.name in self.game.NSPiles:
			self.game.dp.send(signal='return', player=self, card=card)
			self.game.NSPiles[card.name].append(card)
	def discard(self, position = 0, **kwargs):
		discardedCard = self.hand.pop(position)
		self.discardCard(discardedCard, **kwargs)
	def discardCard(self, card, **kwargs):
		if not card.onDiscard(self) and not self.game.dp.send(signal='discard', player=self, card=card): self.discardPile.append(card)
	def revealPosition(self, position = 0, **kwargs):
		if kwargs.get('fromZ', self.hand)==self.library and not self.library:
			self.reshuffle()
			if not self.library: return
		if not kwargs.get('fromZ', self.hand): return
		self.game.dp.send(signal='reveal', player=self, card=kwargs.get('fromZ', self.hand)[position], position=position, fromZ=kwargs.get('fromZ', self.hand).name)
		return kwargs.get('fromZ', self.hand)[position]
	def reveal(self, card, **kwargs):
		self.game.dp.send(signal='reveal', player=self, card=card, fromZ=kwargs.get('fromZ', self.hand).name, **kwargs)
	def discardHand(self, **kwargs):
		while self.hand:
			self.discard()
	def resetValues(self, **kwargs):
		self.coins = 0
		self.potions = 0
		self.actions = 1
		self.buys = 1
	def endTurn(self, **kwargs):
		self.game.dp.send(signal='endTurn', player=self)
		self.discardHand()
		self.destroyAll()
		self.draw(amnt=self.eotdraw)
		self.eotdraw = 5
		self.resetValues()
		self.game.dp.send(signal='turnEnded', player=self)
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
	def take(self, card, **kwargs):
		self.game.dp.send(signal='take', player=self, card=card, fromz=kwargs.get('fromz', None))
		card.owner = self
		card.onGain(self)
		kwargs.get('to', self.discardPile).append(card)
	def gain(self, card, **kwargs):
		if card and not card.onGain(self) and not self.game.dp.send(signal='gain', player=self, card=card, fromz=kwargs.get('fromz', None), kwargs=kwargs):
			card.owner = self
			kwargs.get('to', self.discardPile).append(card)
	def gainFromPile(self, pile, **kwargs):
		self.gain(pile.gain(), fromz=pile, **kwargs)
	def takeFromPile(self, pile, **kwargs):
		self.take(pile.gain(), fromz=pile, **kwargs)
	def buy(self, pile, **kwargs):
		if pile and self.buys>0 and pile[-1].getPrice(self)<=self.coins and pile[-1].getPotionPrice(self)<=self.potions and not self.game.dp.send(signal='tryBuy', player=self, pile=pile, card = pile.viewTop()):
			self.game.dp.send(signal='buy', player=self, pile=pile, card = pile.viewTop())
			self.buys -= 1
			self.coins -= pile[-1].getPrice(self)
			self.potions -= pile[-1].getPotionPrice(self)
			self.gain(pile.gain(), fromz=pile)
	def playAction(self, card, **kwargs):
		self.game.dp.send(signal='playAction', player=self, card=card)
		card.onPlay(self)
	def playTreasure(self, card, **kwargs):
		self.game.dp.send(signal='playTreasure', player=self, card=card)
		card.onPlay(self)
	def attack(self, attack, source, **kwargs):
		if self.game.dp.send(signal='attack', player=self, card=source, attack=attack, **kwargs): return
		attack(self, **kwargs)
	def addCoin(self, **kwargs):
		self.game.dp.send(signal='addCoin', player=self, amnt=kwargs.get('amnt', 1))
		self.coins += kwargs.get('amnt', 1)
	def addBuy(self, **kwargs):
		self.game.dp.send(signal='addBuy', player=self, amnt=kwargs.get('amnt', 1))
		self.buys += kwargs.get('amnt', 1)
	def addAction(self, **kwargs):
		self.game.dp.send(signal='addAction', player=self, amnt=kwargs.get('amnt', 1))
		self.actions += kwargs.get('amnt', 1)
	def addVictory(self, **kwargs):
		self.game.dp.send(signal='addVictory', player=self, amnt=kwargs.get('amnt', 1))
		self.victories += kwargs.get('amnt', 1)
	
class Token(object):
	name = 'baseToken'
	def __init__(self, game, **kwargs):
		self.owner = kwargs.get('owner', None)
		self.game = game
		self.types = []
	def onAddPile(self, pile, **kwargs):
		pass
	def onLeavePile(self, pile, **kwargs):
		pass
	
class Pile(CPile):
	def __init__(self, cardType, game, *args, **kwargs):
		super(Pile, self).__init__(*args, **kwargs)
		self.game = game
		self.cardType = cardType
		self.maskot = cardType(game)
		self.terminator = kwargs.get('terminator', False)
		self.maskot.onPileCreate(self, game) #X fucking D
		self.name = self.maskot.name
		self.tokens = []
		for card in self:
			game.allCards.append(card)
	def gain(self, **kwargs):
		if not self: return
		popped = self.pop()
		if not self:
			self.game.emptyPiles.append(self)
			if self.terminator: self.game.emptyTerminatorPiles += 1
		return popped
	def getView(self):
		return self.name+': '+str(len(self))
	def addToken(self, token, game, **kwargs):
		game.dp.send(signal='addToken', pile=self, token=token)
		token.owner = self
		token.onAddPile(self)
		self.tokens.append(token)
	def removeToken(self, token, game, **kwargs):
		game.dp.send(signal='removeToken', pile=self, token=token)
		token.onLeavePile(self)
		token.owner = None
		
class CardAdd(object):
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(10):
			pile.append(type(self)(game))
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
	
class Card(object):
	name = 'BaseCard'
	def __init__(self, game, **kwargs):
		if not hasattr(self, 'types'): self.types = []
		self.price = kwargs.get('price', 0)
		self.potionPrice = kwargs.get('potionPrice', 0)
		self.owner = None

class Treasure(Card):
	def __init__(self, game, **kwargs):
		super(Treasure, self).__init__(game, **kwargs)
		self.value = 1
		self.types.append('TREASURE')
	def onPlay(self, player, **kwargs):
		super(Treasure, self).onPlay(player, **kwargs)
		player.addCoin(amnt=self.value)
	def getValue(self, **kwargs):
		return np.max((self.value, 0))
		
class Victory(Card):
	def __init__(self, game, **kwargs):
		super(Victory, self).__init__(game, **kwargs)
		self.value = 1
		self.types.append('VICTORY')
	def onGameEnd(self, player, **kwargs):
		player.addVictory(amnt=self.value)
	def onPileCreate(self, pile, game, **kwargs):
		if len(game.players)>2:
			amnt = 12
		else:
			amnt = 8
		for i in range(amnt):
			pile.append(type(self)(game))
		
class Action(Card):
	def __init__(self, game, **kwargs):
		super(Action, self).__init__(game, **kwargs)
		self.types.append('ACTION')
		
class Cursed(Card):
	def __init__(self, game, **kwargs):
		super(Cursed, self).__init__(game, **kwargs)
		self.value = -1
		self.types.append('CURSED')
	def onGameEnd(self, player, **kwargs):
		player.addVictory(amnt=self.value)
		
class Reaction(object):
	def __init__(self, game, **kwargs):
		self.types.append('REACTION')
		self.signal = 'noSignal'
	def trigger(self, signal, **kwargs):
		pass
	def connect(self, **kwargs):
		if 'game' in kwargs: game=kwargs['game']
		else: game = self.owner.game
		game.dp.connect(self.trigger, signal=self.signal)
	def disconnect(self, **kwargs):
		if 'game' in kwargs: game=kwargs['game']
		else: game = self.owner.game
		game.dp.connect(self.trigger, signal=self.signal)
		
class Attack(object):
	def __init__(self, game, **kwargs):
		self.types.append('ATTACK')
		
class Duration(object):
	def __init__(self, game, **kwargs):
		self.types.append('DURATION')
		self.age = 0
		self.nexts = []
	def onPlay(self, player, **kwargs):
		self.nexts.append(self.next)
		player.game.dp.connect(self.nextage, signal='startTurn')
		self.age = 0
	def onDestroy(self, player, **kwargs):
		if self.age<1: return True
	def onLeavePlay(self, player, **kwargs):
		player.game.dp.disconnect(self.nextage, signal='startTurn')
	def nextage(self, signal, **kwargs):
		if not kwargs['player']==self.owner: return
		self.age+=1
		while self.nexts:
			self.owner.game.dp.send(signal='duration', card=self)
			self.nexts.pop()()
	def next(self, **kwargs):
		pass
	
class Reserve(CardAdd):
	def __init__(self, game, **kwargs):
		self.types.append('RESERVE')
		self.triggerSignal = ''
	def onPlay(self, player, **kwargs):
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.mats['Tavern'].append(player.inPlay.pop(i))
				break
		player.game.dp.connect(self.trigger, signal=self.triggerSignal)
	def requirements(self, **kwargs):
		return self.owner==kwargs['player']
	def trigger(self, signal, **kwargs):
		print(self.name, 'TRIGGERED')
		if not (self.requirements(**kwargs) and self.owner.user(('no', 'yes'), 'Call '+self.name)): return
		for i in range(len(self.owner.mats['Tavern'])):
			if self.owner.mats['Tavern'][i]==self:
				self.owner.inPlay.append(self.owner.mats['Tavern'].pop(i))
				self.owner.game.dp.disconnect(self.trigger, signal=self.triggerSignal)
				self.call(signal, **kwargs)
				return
	def call(self, signal, **kwargs):
		self.owner.game.dp.send(signal='call', card=self)
		pass
	def onPileCreate(self, pile, game, **kwargs):
		super(Reserve, self).onPileCreate(pile, game, **kwargs)
		game.addMat('Tavern')
		
class Traveler(CardAdd):
	def __init__(self, game, **kwargs):
		self.types.append('TRAVELER')
		self.morph = None
	def onDestroy(self, player, **kwargs):
		if not (player.game.NSPiles[self.morph.name].viewTop() and player.user(('no', 'yes'), 'Upgrade '+self.name)): return
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.returnCard(player.inPlay.pop(i))
				break
		player.takeFromPile(player.game.NSPiles[self.morph.name])
	def onPileCreate(self, pile, game, **kwargs):
		super(Traveler, self).onPileCreate(pile, game, **kwargs)
		game.require(self.morph)
		
if __name__=='__main__':
	random.seed()