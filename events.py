from dombase import *

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
		player.minusCard = True
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
		
adventuresEvents = [Alms, Borrow, Quest, Save, ScoutingParty]