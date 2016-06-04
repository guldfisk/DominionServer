from cards import *

class Alms(DEvent):
	name = 'Alms'
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		for card in player.inPlay:
			if 'TREASURE' in card.types: return
		player.gainCostingLessThan(5, canBreak=False)
	
class Borrow(DEvent):
	name = 'Borrow'
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		player.resolveEvent(AddBuy)
		player.resolveEvent(TakeMinusDraw)
		player.resolveEvent(AddCoin)

class Quest(DEvent):
	name = 'Quest'
	def onBuy(self, player, **kwargs):
		choice = player.user(('Attack', 'Two curses', 'Six cards'), 'Choose discard')
		if choice==0:
			card = player.selectCard(message='Choose discard', restriction=lambda o: 'ATTACK' in o.types)
			if not card: return
			player.resolveEvent(Discard, card=card)
		if choice==1:
			cards = player.selectCards(2, message='Choose discard', restriction=lambda o: o.name=='Curse')
			if len(cards)<2: return
			for card in cards: player.resolveEvent(Discard, card=card)
		else:
			cards = player.selectCards(6, message='Choose discard')
			if len(cards)<6: return
			for card in cards: player.resolveEvent(Discard, card=card)
		player.resolveEvent(GainFromPile, frm=player.game.piles['Gold'])

class Save(DEvent):
	name = 'Save'
	def __init__(self, game, **kwargs):
		super(Save, self).__init__(game, **kwargs)
		self.coinPrice.set(1)
		game.addMat('Saving')
		self.session.connectCondition(Trigger, trigger='startTurn', source=self, resolve=self.resolveBegin)
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		player.resolveEvent(AddBuy)
		card = player.selectCard(message='Choose save')
		if not card: return
		player.resolveEvent(MoveCard, frm=player.hand, to=player.mats['Saving'], card=card)
	def resolveBegin(self, **kwargs):
		for card in copy.copy(kwargs['player'].mats['Saving']): kwargs['player'].resolveEvent(MoveCard, frm=kwargs['player'].mats['Saving'], to=kwargs['player'].hand, card=card)
		
class ScoutingParty(DEvent):
	name = 'Scouting Party'
	def __init__(self, game, **kwargs):
		super(ScoutingParty, self).__init__(game, **kwargs)
		self.coinPrice.set(2)
	def onBuy(self, player, **kwargs):
		player.resolveEvent(AddBuy)
		cards = player.resolveEvent(RequestCards, amnt=5)
		chosen = player.selectCards(3, frm=cards, message='Choose discard')
		for card in chosen: player.resolveEvent(Discard, frm=player.library, card=card)
		remaining = [o for o in cards if not o in chosen]
		while remaining:
			card = player.selectCard(frm=remaining)
			remaining.remove(card)
			player.resolveEvent(MoveCard, frm=player.library, to=player.library, card=card)

class TravelingFair(DEvent):
	name = 'Traveling Fair'
	class TravelingFairReplace(ReplaceThisTurn):
		name = 'TravelingFairReplace'
		defaultTrigger = 'Gain'
		def condition(self, **kwargs):
			return kwargs['player']==self.owner
		def resolve(self, event, **kwargs):
			return event.spawnClone(to=self.owner.library).resolve()
	def __init__(self, game, **kwargs):
		super(TravelingFair, self).__init__(game, **kwargs)
		self.coinPrice.set(2)
	def onBuy(self, player, **kwargs):
		player.resolveEvent(AddBuy, amnt=2)
		self.session.connectCondition(self.TravelingFairReplace, source=self, owner=player)

class Bonfire(DEvent):
	name = 'Bonfire'
	def __init__(self, game, **kwargs):
		super(Bonfire, self).__init__(game, **kwargs)
		self.coinPrice.set(3)
	def onBuy(self, player, **kwargs):
		cards = player.selectCards(2, frm=player.inPlay, message='Choose trash')
		for card in cards: player.resolveEvent(Trash, frm=player.inPlay, card=card)
		
class Expedition(DEvent):
	name = 'Expedition'
	def __init__(self, game, **kwargs):
		super(Expedition, self).__init__(game, **kwargs)
		self.coinPrice.set(3)
	def onBuy(self, player, **kwargs):
		player.eotdraw += 2
	
def viewEstate(self, **kwargs):
	return Estate.name+'('+self.owner.mats['InheritanceMat'].viewTop().name+')'
	
class EstateTurner(object):
	def turnEstate(self, estate, values, **kwargs):
		estate.disconnect()
		estate.card.currentValues = type(values)(self.session, card=estate.card)
		estate.card.currentValues.name = Estate.name
		estate.card.currentValues.types.add('VICTORY')
		estate.card.currentValues.view = types.MethodType(viewEstate, estate.card.currentValues)
		#estate.card.currentValues.view = self.viewEstate
	def unturnEstate(self, estate, **kwargs):
		estate.card.disconnect()
		estate.card.currentValues = Estate(self.session, card=estate.card)
		
class InheritanceToken(Token, EstateTurner):
	name = 'Inheritance Token'
	def __init__(self, session, **kwargs):
		super(InheritanceToken, self).__init__(session, **kwargs)
		session.connectCondition(Replacement, trigger='GainOwnership', source=self, resolve=self.resolveGainOwner, condition=self.conditionOwner)
		session.connectCondition(Replacement, trigger='LooseOwnership', source=self, resolve=self.resolveLooseOwner, condition=self.conditionOwner)
	def conditionOwner(self, **kwargs):
		return self.owner and kwargs['player']==self.playerOwner and kwargs['card'].frmPile.name==Estate.name
	def resolveGainOwner(self, event, **kwargs):
		self.turnEstate(event.card, self.owner.printedValues)
		return event.spawnClone().resolve()
	def resolveLooseOwner(self, event, **kwargs):
		self.unturnEstate(event.card)
		return event.spawnClone().resolve()
	
class Inheritance(DEvent, EstateTurner):
	name = 'Inheritance'
	def __init__(self, session, **kwargs):
		super(Inheritance, self).__init__(session, **kwargs)
		self.coinPrice.set(7)
		session.addMat('InheritanceMat')
		session.addToken(InheritanceToken)
	def onBuy(self, player, **kwargs):
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='BuyDEvent' and player.session.events[i][1]['card'].name==self.name and player.session.events[i][1]['player']==player: return False
		pile = player.pileCostingLess(5, canBreak=False, restriction=lambda o: 'ACTION' in o.types and not 'VICTORY' in o.types)
		card = pile.viewTop()
		if not card: return
		player.resolveEvent(MoveCard, frm=pile, to=player.mats['InheritanceMat'], card=card)
		player.tokens['Inheritance Token'].owner=card
		for owned in player.owns:
			if owned.frmPile.name=='Estate': self.turnEstate(owned, card.printedValues)
		
adventuresDEvents = [Alms, Inheritance, Borrow, Quest, Save, ScoutingParty, TravelingFair, Bonfire, Expedition]