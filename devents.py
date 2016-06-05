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
		player.resolveEvent(GainFromPile, frm=player.session.piles['Gold'])

class Save(DEvent):
	name = 'Save'
	def __init__(self, session, **kwargs):
		super(Save, self).__init__(session, **kwargs)
		self.coinPrice.set(1)
		session.addMat('Saving')
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
	def __init__(self, session, **kwargs):
		super(ScoutingParty, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(TravelingFair, self).__init__(session, **kwargs)
		self.coinPrice.set(2)
	def onBuy(self, player, **kwargs):
		player.resolveEvent(AddBuy, amnt=2)
		self.session.connectCondition(self.TravelingFairReplace, source=self, owner=player)

class Bonfire(DEvent):
	name = 'Bonfire'
	def __init__(self, session, **kwargs):
		super(Bonfire, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onBuy(self, player, **kwargs):
		cards = player.selectCards(2, frm=player.inPlay, message='Choose trash')
		for card in cards: player.resolveEvent(Trash, frm=player.inPlay, card=card)
		
class Expedition(DEvent):
	name = 'Expedition'
	def __init__(self, session, **kwargs):
		super(Expedition, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onBuy(self, player, **kwargs):
		player.eotdraw += 2
	
class MinusCost(Token):
	name = 'Minus Cost'
	def __init__(self, session, **kwargs):
		super(MinusCost, self).__init__(session, **kwargs)
		self.connectCondition(ADStatic, trigger='coinPrice', source=self, resolve=self.resolveAccess, condition=self.conditionAccess)
	def conditionAccess(self, **kwargs):
		return self.playerOwner and self.owner and hasattr(kwargs['master'], 'types') and kwargs['master'].frmPile==self.owner and self.playerOwner==self.session.activePlayer
	def resolveAccess(self, val, **kwargs):
		if val<2: return 0
		return val-2

class TrashingToken(Token):
	name = 'Trashing Token'
	def __init__(self, session, **kwargs):
		super(TrashingToken, self).__init__(session, **kwargs)
		self.connectCondition(Trigger, trigger='Buy', source=self, resolve=self.resolveBuy, condition=self.conditionBuy)
	def conditionBuy(self, **kwargs):
		return self.playerOwner and self.owner and kwargs['card'].frmPile==self.owner and kwargs['player']==self.playerOwner
	def resolveBuy(self, **kwargs):
		card = self.playerOwner.selectCard(optional=True, message='Choose trash')
		if card: self.playerOwner.resolveEvent(Trash, frm=self.playerOwner.hand, card=card)
		
class Ferry(DEvent):
	name = 'Ferry'
	def __init__(self, session, **kwargs):
		super(Ferry, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
		session.addToken(MinusCost)
	def onBuy(self, player, **kwargs):
		token = player.tokens['Minus Cost']
		pile = player.getPile(restriction=lambda o: 'ACTION' in o.types)
		if token.owner: player.resolveEvent(MoveToken, frm=token.owner.tokens, to=pile, token=token)
		else: player.resolveEvent(AddToken, to=pile, token=token)

class Plan(DEvent):
	name = 'Plan'
	def __init__(self, session, **kwargs):
		super(Plan, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
		session.addToken(TrashingToken)
	def onBuy(self, player, **kwargs):
		token = player.tokens['Trashing Token']
		pile = player.getPile(restriction=lambda o: 'ACTION' in o.types)
		if token.owner: player.resolveEvent(MoveToken, frm=token.owner.tokens, to=pile, token=token)
		else: player.resolveEvent(AddToken, to=pile, token=token)

class Mission(DEvent):
	name = 'Mission'
	class MissionReplace(ReplaceThisTurn):
		name = 'MissionReplace'
		defaultTrigger = 'Purchase'
		def condition(self, **kwargs):
			return kwargs['player']==self.owner
	def __init__(self, session, **kwargs):
		super(Mission, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onBuy(self, player, **kwargs):
		if not self.checkBefore(player): return
		turns = 0
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[0]=='startTurn':
				if self.session.event[1]['player']==self: turns+=1
				else: break
		if turns>1: return
		player.session.extraTurns.append((self.missionTurn, {'player': player}))
	def missionTurn(self, **kwargs):
		self.connectCondition(self.MissionReplace, source=self, owner=kwargs['player'])
		self.session.activePlayer = kwargs['player']
		self.session.turnFlag = 'mission'
		kwargs['player'].resetValues()
		self.session.dp.send(signal='startTurn', player=kwargs['player'], flags=kwargs['player'].session.turnFlag)
		kwargs['player'].session.resolveTriggerQueue()
		kwargs['player'].actionPhase()
		kwargs['player'].treasurePhase()
		kwargs['player'].buyPhase()
		kwargs['player'].endTurn()
		
class Pilgrimage(DEvent):
	name = 'Pilgrimage'
	def __init__(self, session, **kwargs):
		super(Pilgrimage, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onBuy(self, player, **kwargs):
		if not (self.checkBefore(player) and player.resolveEvent(FlipJourney)): return
		seen = set()
		cards = player.selectCards(3, frm=[o for o in player.inPlay if not o.name in seen and not seen.add(o.name)], optional=True, message='Choose gain')
		for card in cards: player.resolveEvent(GainFromPile, frm=self.session.piles[card.name])

class Ball(DEvent):
	name = 'Ball'
	def __init__(self, session, **kwargs):
		super(Ball, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onBuy(self, player, **kwargs):
		player.resolveEvent(TakeMinusCoin)
		for i in range(2): player.gainCostingLessThan(5)
		
class Raid(DEvent):
	name = 'Raid'
	def __init__(self, session, **kwargs):
		super(Raid, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onBuy(self, player, **kwargs):
		for card in player.inPlay:
			if card.name=='Silver': player.resolveEvent(GainFromPile, frm=player.session.piles['Silver'])
		for aplayer in player.session.getOtherPlayers(player): aplayer.resolveEvent(TakeMinusCard)

class Seaway(DEvent):
	name = 'Seaway'
	def __init__(self, session, **kwargs):
		super(Seaway, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		session.addToken(PlusBuy)
	def onBuy(self, player, **kwargs):
		token = player.tokens['Plus Buy Token']
		pile = player.getPile(restriction=lambda o: 'ACTION' in o.types)
		player.resolveEvent(GainFromPile, frm=pile)
		if token.owner: player.resolveEvent(MoveToken, frm=token.owner.tokens, to=pile, token=token)
		else: player.resolveEvent(AddToken, to=pile, token=token)

class Trade(DEvent):
	name = 'Trade'
	def __init__(self, session, **kwargs):
		super(Trade, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onBuy(self, player, **kwargs):		
		cards = player.selectCards(2, optional=True, message='Choose trash')
		for card in cards: player.resolveEvent(Trash, frm=player.hand, card=card)
		for card in cards: player.resolveEvent(GainFromPile, frm=self.session.piles['Silver'])
		
class LostArts(DEvent):
	name = 'Lost Arts'
	def __init__(self, session, **kwargs):
		super(LostArts, self).__init__(session, **kwargs)
		self.coinPrice.set(6)
		session.addToken(PlusAction)
	def onBuy(self, player, **kwargs):		
		token = player.tokens['Plus Action Token']
		pile = player.getPile(restriction=lambda o: 'ACTION' in o.types)
		if token.owner: player.resolveEvent(MoveToken, frm=token.owner.tokens, to=pile, token=token)
		else: player.resolveEvent(AddToken, to=pile, token=token)

class Training(DEvent):
	name = 'Training'
	def __init__(self, session, **kwargs):
		super(Training, self).__init__(session, **kwargs)
		self.coinPrice.set(6)
		session.addToken(PlusCoin)
	def onBuy(self, player, **kwargs):		
		token = player.tokens['Plus Coin Token']
		pile = player.getPile(restriction=lambda o: 'ACTION' in o.types)
		if token.owner: player.resolveEvent(MoveToken, frm=token.owner.tokens, to=pile, token=token)
		else: player.resolveEvent(AddToken, to=pile, token=token)

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
		
class Pathfinding(DEvent):
	name = 'Pathfinding'
	def __init__(self, session, **kwargs):
		super(Pathfinding, self).__init__(session, **kwargs)
		self.coinPrice.set(8)
		session.addToken(PlusCard)
	def onBuy(self, player, **kwargs):		
		token = player.tokens['Plus Card Token']
		pile = player.getPile(restriction=lambda o: 'ACTION' in o.types)
		if token.owner: player.resolveEvent(MoveToken, frm=token.owner.tokens, to=pile, token=token)
		else: player.resolveEvent(AddToken, to=pile, token=token)
	
adventuresDEvents = [Alms, Borrow, Quest, Save, ScoutingParty, TravelingFair, Bonfire, Expedition, Ferry, Plan, Mission, Pilgrimage, Ball, Raid, Seaway, Trade, LostArts, Training, Inheritance, Pathfinding]

class Summon(DEvent):
	name = 'Summon'
	def __init__(self, session, **kwargs):
		super(Summon, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		session.addMat('Summoning')
		self.connectCondition(Trigger, trigger='startTurn', source=self, resolve=self.resolveBegin)
		self.connectCondition(Replacement, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
	def onBuy(self, player, **kwargs):
		player.gainCostingLessThan(5, source=self, restriction=lambda o: 'ACTION' in o.types)
	def resolveBegin(self, **kwargs):
		for card in copy.copy(kwargs['player'].mats['Summoning']): kwargs['player'].resolveEvent(CastCard, frm=kwargs['player'].mats['Summoning'], card=card)
	def conditionGain(self, **kwargs):
		return kwargs['source']==self
	def resolveGain(self, event, **kwargs):
		event.spawnClone().resolve()
		return event.spawn(MoveCard, frm=event.to, to=event.player.mats['Summoning']).resolve()
	
promoDEvents = [Summon]

class Triumph(DEvent):
	name = 'Triumph'
	def __init__(self, session, **kwargs):
		super(Triumph, self).__init__(session, **kwargs)
		self.debtPrice.set(5)
	def onBuy(self, player, **kwargs):		
		if not player.resolveEvent(GainFromPile, frm=self.session.piles['Estate']): return
		gained = 0
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='Gain' and self.session.events[i][1]['player']==player: gained+=1
			elif self.session.events[i][0]=='startTurn': break
		player.resolveEvent(AddVictory, amnt=gained)
		
class Windfall(DEvent):
	name = 'Windfall'
	def __init__(self, session, **kwargs):
		super(Windfall, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onBuy(self, player, **kwargs):		
		if not player.library and not player.discardPile:
			for i in range(3): player.resolveEvent(GainFromPile, frm=self.session.piles['Gold'])
		
class Dominate(DEvent):
	name = 'Dominate'
	def __init__(self, session, **kwargs):
		super(Dominate, self).__init__(session, **kwargs)
		self.coinPrice.set(14)
	def onBuy(self, player, **kwargs):		
		if player.resolveEvent(GainFromPile, frm=self.session.piles['Province']): player.resolveEvent(AddVictory, amnt=9)
		
empiresDEvents = [Triumph, Windfall, Dominate]