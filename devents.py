from cards import *

class Alms(DEvent):
	name = 'Alms'
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		for card in player.inPlay:
			if 'TREASURE' in card.types: return
		options = []
		player.gainCostingLessThan(5, canBreak=False)
	
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
		
adventuresDEvents = [Alms, Inheritance]