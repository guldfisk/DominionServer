from cards import *

class Alms(Event):
	name = 'Alms'
	def __init__(self, game, **kwargs):
		super(Alms, self).__init__(game, **kwargs)
		self.price = 0
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		for card in player.inPlay:
			if 'TREASURE' in card.types: return
		options = []
		for pile in player.game.piles:
			if player.game.piles[pile].viewTop() and player.game.piles[pile].viewTop().getPrice(player)<5 and player.game.piles[pile].viewTop().getPotionPrice(player)<1:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.game.piles[options[choice]])

class Borrow(Event):
	name = 'Borrow'
	def __init__(self, game, **kwargs):
		super(Borrow, self).__init__(game, **kwargs)
		self.price = 0
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		player.addBuy()
		player.minusDraw = True
		player.addCoin()
		
class Quest(Event):
	name = 'Quest'
	def __init__(self, game, **kwargs):
		super(Quest, self).__init__(game, **kwargs)
		self.price = 0
	def onBuy(self, player, **kwargs):
		choice = player.user(('Attack', 'Two curses', 'Six cards'), 'Choose discard')
		if choice==0:
			options = []
			for i in range(len(player.hand)):
				if 'ATTACK' in player.hand[i]: options.append(i)
			if not options: return
			choice = player.user([player.hand[o] for o in options], 'Choose discard')
			player.discard(options[choice])
		if choice==1:
			curses = 0
			for card in player.hand:
				if card.name=='Curse':
					curses += 1
					if curses>1: break
			if curses<2: return
			for i in range(2):
				for n in range(len(player.hand)):
					if player.hand[n].name=='Curse':
						player.discard(n)
						break
		else:
			if len(player.hand)<6: return
			for i in range(6): player.discard(player.user([o.name for o in player.hand], 'Choose discard '+str(i+1)))
		player.gainFromPile(player.game.piles['Gold'])

class Save(Event):
	name = 'Save'
	def __init__(self, game, **kwargs):
		super(Save, self).__init__(game, **kwargs)
		self.price = 1
		game.addMat('Saving')
		game.dp.connect(self.trigger, signal='startTurn')
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		player.addBuy()
		player.mats['Saving'].append(player.hand.pop(player.user([o.name for o in player.hand], 'Choose save')))
	def trigger(self, signal, **kwargs):
		while kwargs['player'].mats['Saving']: kwargs['player'].hand.append(kwargs['player'].mats['Saving'].pop())
		
class ScoutingParty(Event):
	name = 'Scouting Party'
	def __init__(self, game, **kwargs):
		super(ScoutingParty, self).__init__(game, **kwargs)
		self.price = 2
	def onBuy(self, player, **kwargs):
		player.addBuy()
		cards = player.getCards(5)
		for i in range(3):
			if not cards: break
			player.discardCard(cards.pop(player.user([o.name for o in cards], 'Choose discard '+str(i+1))))
		while cards: player.library.append(cards.pop(player.user([o.name for o in cards], 'Put card back')))
		
class TravelingFair(Event):
	name = 'Traveling Fair'
	def __init__(self, game, **kwargs):
		super(TravelingFair, self).__init__(game, **kwargs)
		self.price = 2
		self.connectedPlayers = []
		game.dp.connect(self.reset, signal='startTurn')
		game.dp.connect(self.trigger, signal='gain')
	def onBuy(self, player, **kwargs):
		player.addBuy(amnt=2)
		self.connectedPlayers.append(player)
	def reset(self, signal, **kwargs):
		self.connectedPlayers[:] = []
	def trigger(self, signal, **kwargs):
		if kwargs['player'] in self.connectedPlayers and kwargs['player'].user(('no', 'Top'), 'Use Traveling Fair'): kwargs['kwargs']['to'] = kwargs['player'].library

class Bonfire(Event):
	name = 'Bonfire'
	def __init__(self, game, **kwargs):
		super(Bonfire, self).__init__(game, **kwargs)
		self.price = 3
	def onBuy(self, player, **kwargs):
		for i in range(2):
			if not player.inPlay: break
			choice = player.user([o.name for o in player.inPlay]+['End trash'], 'Choose trash '+str(i))
			if choice+1>len(player.inPlay): break
			player.inPlay[choice].onLeavePlay(player)
			player.trashCard(player.inPlay.pop(choice))

class Expedition(Event):
	name = 'Expedition'
	def __init__(self, game, **kwargs):
		super(Expedition, self).__init__(game, **kwargs)
		self.price = 3
	def onBuy(self, player, **kwargs):
		player.eotdraw += 2

class MinusCost(Token):
	name = 'Minus Cost Token'
	def start(self, signal, **kwargs):
		if self.playerOwner==kwargs['player']:
			for card in self.owner.game.allCards:	
				if card.name==self.owner.maskot.name: card.price -= 2
	def end(self, signal, **kwargs):
		if self.playerOwner==kwargs['player']:
			for card in self.owner.game.allCards: 
				if card.name==self.owner.maskot.name: card.price += 2
	def connect(self, game, **kwargs):
		game.dp.connect(self.start, signal='startTurn')
		game.dp.connect(self.end, signal='endTurn')
		self.start('startTurn', player=self.playerOwner)
	def disconnect(self, game, **kwargs):
		self.end('endTurn', player=self.playerOwner)
		game.dp.disconnect(self.start, signal='startTurn')
		game.dp.disconnect(self.end, signal='endTurn')
	def onAddPile(self, pile, **kwargs):
		self.connect(pile.game, **kwargs)
	def onLeavePile(self, pile, **kwargs):
		self.disconnect(pile.game, **kwargs)

class TrashingToken(Token):
	name = 'Trashing Token'
	def trigger(self, signal, **kwargs):
		if not (kwargs['pile']==self.owner and kwargs['player']==self.playerOwner and kwargs['player'].hand): return
		choice = kwargs['player'].user([o.name for o in kwargs['player'].hand]+['No trash'], 'Choose trash')
		if choice+1>len(kwargs['player'].hand): return
		kwargs['player'].trash(choice)
	def connect(self, game, **kwargs):
		game.dp.connect(self.trigger, signal='buy')
	def dicconnect(self, game, **kwargs):
		game.dp.disconnect(self.trigger, signal='buy')
	def onAddPile(self, pile, **kwargs):
		self.connect(pile.game)
	def onLeavePile(self, pile, **kwargs):
		self.disconnect(pile.game)
		
class Ferry(Event):
	name = 'Ferry'
	def __init__(self, game, **kwargs):
		super(Ferry, self).__init__(game, **kwargs)
		self.price = 3
		game.addToken(MinusCost)
	def onBuy(self, player, **kwargs):
		options = []
		for pile in self.game.piles:
			if 'ACTION' in self.game.piles[pile].maskot.types: options.append(pile)
		if not options: return
		pile = options[player.user(options, 'Choose pile')]
		token = player.tokens['Minus Cost Token']
		if token.owner:
			for i in range(len(token.owner.tokens)):
				if token==token.owner.tokens[i]:
					tok = token.owner.tokens.pop(i)
					token.owner.removeToken(tok, self.game)
					break
		self.game.piles[pile].addToken(token, self.game)
		
class Plan(Event):
	name = 'Plan'
	def __init__(self, game, **kwargs):
		super(Plan, self).__init__(game, **kwargs)
		self.price = 3
		game.addToken(TrashingToken)
	def onBuy(self, player, **kwargs):
		options = []
		for pile in self.game.piles:
			if 'ACTION' in self.game.piles[pile].maskot.types: options.append(pile)
		if not options: return
		pile = options[player.user(options, 'Choose pile')]
		token = player.tokens['Trashing Token']
		if token.owner:
			for i in range(len(token.owner.tokens)):
				if token==token.owner.tokens[i]:
					tok = token.owner.tokens.pop(i)
					token.owner.removeToken(tok, self.game)
					break
		self.game.piles[pile].addToken(token, self.game)
		
class Mission(Event):
	name = 'Mission'
	def __init__(self, game, **kwargs):
		super(Mission, self).__init__(game, **kwargs)
		self.price = 4
		game.addToken(TrashingToken)
		self.missionaries = []
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		player.game.delayedActions.append((self.missionTurn, {'player': player}))
	def trigger(self, signal, **kwargs):
		if kwargs['player'] in self.missionaries: return True
	def missionTurn(self, **kwargs):
		turns = 0
		for i in range(len(self.game.events)-1, -1, -1):
			if self.game.events[0]=='startTurn':
				if self.game.event[1]['player']==self: turns+=1
				else: break
		if turns>1: return
		self.missionaries.append(kwargs['player'])
		self.game.dp.connect(self.trigger, signal='tryBuy')
		self.game.activePlayer = self.missionaries[0]
		self.game.turnFlag = 'mission'
		kwargs['player'].resetValues()
		self.game.dp.send(signal='startTurn', player=self.missionaries[0], flag=self.game.turnFlag)
		kwargs['player'].actionPhase()
		kwargs['player'].treasurePhase()
		kwargs['player'].buyPhase()
		kwargs['player'].endTurn()
		self.missionaries[:] = []
		self.game.dp.disconnect(self.trigger, signal='tryBuy')

class Pilgrimage(Event):
	name = 'Pilgrimage'
	def __init__(self, game, **kwargs):
		super(Pilgrimage, self).__init__(game, **kwargs)
		self.price = 4
	def onBuy(self, player, **kwargs):
		if not (self.checkBefore(player) and player.flipJourney()): return
		chosen = set()
		for i in range(3):
			options = list(set([o.name for o in player.inPlay])-chosen)
			if not options: break
			choice = player.user(options+['No gain'], 'Choose gain')
			if choice+1>len(options): break
			chosen.add(options[choice])
		for choice in chosen: player.gainFromPile(player.game.piles[choice])
			
class Ball(Event):
	name = 'Ball'
	def __init__(self, game, **kwargs):
		super(Ball, self).__init__(game, **kwargs)
		self.price = 5
	def onBuy(self, player, **kwargs):
		player.minusCoin = True
		for i in range(2):
			options = []
			for pile in player.game.piles:
				if player.game.piles[pile].viewTop() and player.game.piles[pile].viewTop().getPrice(player)<5 and player.game.piles[pile].viewTop().getPotionPrice(player)<1:
					options.append(pile)
			if not options: return
			choice = player.user(options+['No gain'], 'Choose gain '+str(i+1))
			if choice+1>len(options): break
			player.gainFromPile(player.game.piles[options[choice]])
		
class Raid(Event):
	name = 'Raid'
	def __init__(self, game, **kwargs):
		super(Raid, self).__init__(game, **kwargs)
		self.price = 5
	def onBuy(self, player, **kwargs):
		for card in player.inPlay:
			if card.name=='Silver': player.gainFromPile(player.game.piles['Silver'])
		for aplayer in player.game.getPlayers(player):
			if not player==aplayer: aplayer.minusCard = True

class Seaway(Event):
	name = 'Seaway'
	def __init__(self, game, **kwargs):
		super(Seaway, self).__init__(game, **kwargs)
		self.price = 5
		game.addToken(PlusBuy)
	def onBuy(self, player, **kwargs):
		options = []
		for pile in player.game.piles:
			if player.game.piles[pile].viewTop() and player.game.piles[pile].viewTop().getPrice(player)<5 and player.game.piles[pile].viewTop().getPotionPrice(player)<1:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain '+str(i+1))
		player.gainFromPile(player.game.piles[options[choice]])
		token = player.tokens['Plus Card Token']
		if token.owner:
			for i in range(len(token.owner.tokens)):
				if token==token.owner.tokens[i]:
					tok = token.owner.tokens.pop(i)
					token.owner.removeToken(tok, self.game)
					break
		self.game.piles[pile].addToken(token, self.game)

class Trade(Event):
	name = 'Trade'
	def __init__(self, game, **kwargs):
		super(Trade, self).__init__(game, **kwargs)
		self.price = 5
	def onBuy(self, player, **kwargs):		
		if not player.hand: return
		options = copy.copy(player.hand)
		trashed = []
		for i in range(2):
			choice = player.user([o.name for o in options]+['EndChapel'], 'Choose trash')
			if choice+1>len(options): break
			trashed.append(options.pop(choice))
			if not options: break
		for card in trashed:
			for i in range(len(player.hand)):
				if player.hand[i]==card:
					player.trash(i)
					player.gainFromPile(player.game.piles['Silver'])
					break

class LostArts(Event):
	name = 'Lost Arts'
	def __init__(self, game, **kwargs):
		super(LostArts, self).__init__(game, **kwargs)
		self.price = 6
		game.addToken(PlusAction)
	def onBuy(self, player, **kwargs):		
		options = []
		for pile in self.game.piles:
			if 'ACTION' in self.game.piles[pile].maskot.types: options.append(pile)
		if not options: return
		pile = options[player.user(options, 'Choose pile')]
		token = player.tokens['Plus Action Token']
		if token.owner:
			for i in range(len(token.owner.tokens)):
				if token==token.owner.tokens[i]:
					tok = token.owner.tokens.pop(i)
					token.owner.removeToken(tok, self.game)
					break
		self.game.piles[pile].addToken(token, self.game)
					
class Training(Event):
	name = 'Training'
	def __init__(self, game, **kwargs):
		super(Training, self).__init__(game, **kwargs)
		self.price = 6
		game.addToken(PlusCoin)
	def onBuy(self, player, **kwargs):		
		options = []
		for pile in self.game.piles:
			if 'ACTION' in self.game.piles[pile].maskot.types: options.append(pile)
		if not options: return
		pile = options[player.user(options, 'Choose pile')]
		token = player.tokens['Plus Coin Token']
		if token.owner:
			for i in range(len(token.owner.tokens)):
				if token==token.owner.tokens[i]:
					tok = token.owner.tokens.pop(i)
					token.owner.removeToken(tok, self.game)
					break
		self.game.piles[pile].addToken(token, self.game)
		
class Pathfinding(Event):
	name = 'Pathfinding'
	def __init__(self, game, **kwargs):
		super(Pathfinding, self).__init__(game, **kwargs)
		self.price = 8
		game.addToken(PlusCard)
	def onBuy(self, player, **kwargs):		
		options = []
		for pile in self.game.piles:
			if 'ACTION' in self.game.piles[pile].maskot.types: options.append(pile)
		if not options: return
		pile = options[player.user(options, 'Choose pile')]
		token = player.tokens['Plus Card Token']
		if token.owner:
			for i in range(len(token.owner.tokens)):
				if token==token.owner.tokens[i]:
					tok = token.owner.tokens.pop(i)
					token.owner.removeToken(tok, self.game)
					break
		self.game.piles[pile].addToken(token, self.game)
		
adventuresEvents = [Alms, Borrow, Quest, Save, ScoutingParty, TravelingFair, Bonfire, Expedition, Ferry, Plan, Mission, Pilgrimage, Ball, Raid, Seaway, Trade, LostArts, Training, Pathfinding]