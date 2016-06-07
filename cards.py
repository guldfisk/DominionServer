from dombase import *

class ProHunterDogKeeper(Treasure):
	name = 'Pro Hunter Dog Keeper'
	def __init__(self, session, **kwargs):
		super(ProHunterDogKeeper, self).__init__(session, **kwargs)
		self.coinValue.set(255)
		self.coinPrice.set(0)
	def onPlay(self, player, **kwargs):
		super(ProHunterDogKeeper, self).onPlay(player, **kwargs)
		player.resolveEvent(AddBuy, amnt=255)
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(60): pile.addCard(type(self))

testCards = [ProHunterDogKeeper]
		
class Copper(Treasure):
	name = 'Copper'
	def __init__(self, session, **kwargs):
		super(Copper, self).__init__(session, **kwargs)
		self.coinValue.set(1)
		self.coinPrice.set(0)
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(60): pile.addCard(type(self))
			
class Silver(Treasure):
	name = 'Silver'
	def __init__(self, session, **kwargs):
		super(Silver, self).__init__(session, **kwargs)
		self.coinValue.set(2)
		self.coinPrice.set(3)
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(40): pile.addCard(type(self))
		
class Gold(Treasure):
	name = 'Gold'
	def __init__(self, session, **kwargs):
		super(Gold, self).__init__(session, **kwargs)
		self.coinValue.set(3)
		self.coinPrice.set(6)
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(30): pile.addCard(type(self))
			
class Estate(Victory):
	name = 'Estate'
	def __init__(self, session, **kwargs):
		super(Estate, self).__init__(session, **kwargs)
		self.victoryValue.set(1)
		self.coinPrice.set(2)
	def onPileCreate(self, pile, session, **kwargs):
		if len(session.players)>2: amnt = 12
		else: amnt = 8
		for i in range(amnt+len(session.players)*3): pile.addCard(type(self))
			
class Duchy(Victory):
	name = 'Duchy'
	def __init__(self, session, **kwargs):
		super(Duchy, self).__init__(session, **kwargs)
		self.victoryValue.set(3)
		self.coinPrice.set(5)

class Province(Victory):
	name = 'Province'
	def __init__(self, session, **kwargs):
		super(Province, self).__init__(session, **kwargs)
		self.victoryValue.set(6)
		self.coinPrice.set(8)
	def onPileCreate(self, pile, session, **kwargs):
		super(Province, self).onPileCreate(pile, session)
		pile.terminator = True
			
class Curse(Cursed):
	name = 'Curse'
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(10*max((len(session.players)-1, 1))): pile.addCard(type(self))
			
baseSetBase = [Copper, Silver, Gold, Estate, Duchy, Province, Curse]

class Cellar(Action):
	name = 'Cellar'
	def __init__(self, session, **kwargs):
		super(Cellar, self).__init__(session, **kwargs)
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(Cellar, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction)
		cards = player.selectCards(optional=True, message='Choose discard')
		for card in cards: player.resolveEvent(Discard, frm=player.hand, card=card)
		player.resolveEvent(DrawCards, amnt=len(cards))
		
class Chapel(Action):
	name = 'Chapel'
	def __init__(self, session, **kwargs):
		super(Chapel, self).__init__(session, **kwargs)
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(Chapel, self).onPlay(player, **kwargs)
		for card in player.selectCards(4, optional=True): player.resolveEvent(Trash, frm=player.hand, card=card)
	
class Moat(Action, Reaction):
	name = 'Moat'
	class MoatProtect(DelayedReplacement):
		name = 'MoatProtect'
		defaultTrigger = 'ResolveAttack'
		def condition(self, **kwargs):
			return kwargs['source']==self.enemy
	def __init__(self, session, **kwargs):
		super(Moat, self).__init__(session, **kwargs)
		Reaction.__init__(self, session, **kwargs)
		self.coinPrice.set(2)
		self.connectCondition(Replacement, trigger='PlayCard', source=self.card, resolve=self.resolveReact, condition=self.conditionReact)
	def onPlay(self, player, **kwargs):
		super(Moat, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=2)
	def conditionReact(self, **kwargs):
		return self.owner and self.card in self.owner.hand and 'ATTACK' in kwargs['card'].types and not self.owner==kwargs['player']
	def resolveReact(self, event, **kwargs):
		if self.owner.user(['no', 'yes'], 'Reveal Moat'):
			self.owner.resolveEvent(Reveal, card=self, frm=self.owner.hand)
			self.session.connectCondition(self.MoatProtect, source=self.card, enemy=event.card)
			return event.spawnClone().resolve()
		else: return event.spawnClone().resolve()
		
class Chancellor(Action):
	name = 'Chancellor'
	def __init__(self, session, **kwargs):
		super(Chancellor, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Chancellor, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		if player.user(('no', 'yes'), 'Discard library'): player.resolveEvent(DiscardDeck)
		
class Village(Action):
	name = 'Village'
	def __init__(self, session, **kwargs):
		super(Village, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Village, self).onPlay(player, **kwargs)
		player.resolveEvent(Draw)
		player.resolveEvent(AddAction, amnt=2)
		
class Woodcutter(Action):
	name = 'Woodcutter'
	def __init__(self, session, **kwargs):
		super(Woodcutter, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Woodcutter, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		player.resolveEvent(AddBuy)
	
class Workshop(Action):
	name = 'Workshop'
	def __init__(self, session, **kwargs):
		super(Workshop, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Workshop, self).onPlay(player, **kwargs)
		player.gainCostingLessThan(5)
	
class Bureaucrat(Action, Attack):
	name = 'Bureaucrat'
	def __init__(self, session, **kwargs):
		super(Bureaucrat, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Bureaucrat, self).onPlay(player, **kwargs)
		player.resolveEvent(GainFromPile, frm=player.session.piles['Silver'], to=player.library)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		if not True in ['Victory' in o.types for o in player.hand]:
			for card in player.hand: player.resolveEvent(Reveal, card=card)
			return
		while True:
			card = player.selectCard(message='Choose top')
			if not 'VICTORY' in card.types: continue
			player.resolveEvent(Reveal, card=card)
			player.resolveEvent(MoveCard, frm=player.hand, to=player.library, card=card)
			break

class Feast(Action):
	name = 'Feast'
	def __init__(self, session, **kwargs):
		super(Feast, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Feast, self).onPlay(player, **kwargs)
		player.gainCostingLessThan(6)
		player.resolveEvent(Trash, frm=player.inPlay, card=self.card)
		
class Gardens(Victory):
	name = 'Gardens'
	def __init__(self, session, **kwargs):
		super(Gardens, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onGameEnd(self, player, **kwargs):
		return m.floor(len(player.owns)/10)
		
class Militia(Action, Attack):
	name = 'Militia'
	def __init__(self, session, **kwargs):
		super(Militia, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Militia, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		while len(player.hand)>3:
			card = player.selectCard(message='Choose discard')
			player.resolveEvent(Discard, card=card)

class Moneylender(Action):
	name = 'Moneylender'
	def __init__(self, session, **kwargs):
		super(Moneylender, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Moneylender, self).onPlay(player, **kwargs)
		while True:
			choice = player.selectCard(message='Choose trash')
			if not choice: return
			if card.name=='Copper':
				player.resolveEvent(Trash, card=card, frm=player.hand)
				player.addCoin(amnt=3)
				break

class Remodel(Action):
	name = 'Remodel'
	def __init__(self, session, **kwargs):
		super(Remodel, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Remodel, self).onPlay(player, **kwargs)
		card = player.selectCard(message='Choose trash')
		if not card: return
		player.resolveEvent(Trash, card=card, frm=player.hand)
		player.gainCostingLessThan(3, card=card)
		
class Smithy(Action):
	name = 'Smithy'
	def __init__(self, session, **kwargs):
		super(Smithy, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Smithy, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=3)
		
class Spy(Action, Attack):
	name = 'Spy'
	def __init__(self, session, **kwargs):
		super(Spy, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Spy, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction)
		player.resolveEvent(Draw)
		self.attackAll(player)
	def attack(self, player, **kwargs):
		card = player.resolveEvent(RequestCard)
		if not card: return
		player.resolveEvent(Reveal, card=card)
		if self.owner.user(('Top', 'Discard'), ''):
			player.resolveEvent(Message, content='Spy bottom')
			player.resolveEvent(Discard, frm=player.library, card=card)
		else: player.resolveEvent(Message, content='Spy top')
		
class Thief(Action, Attack):
	name = 'Thief'
	def __init__(self, session, **kwargs):
		super(Thief, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Thief, self).onPlay(player, **kwargs)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		cards = player.resolveEvent(RequestCards, amnt=2)
		options = []
		for card in cards:
			player.resolveEvent(Reveal, card=card)
			if 'TREASURE' in card.types:
				options.append(card)
		choice = None
		if options:
			choice = self.owner.user([o.view() for o in options], 'Choose trash')
			gain = self.owner.user(('No', 'Yes'), 'Gain')
		for card in copy.copy(cards):
			if choice!=None and card==options[choice]:
				self.owner.resolveEvent(Trash, frm=player.library, card=card)
				if gain: self.owner.resolveEvent(Gain, frm=self.owner.session.trash, card=card)
			else: player.resolveEvent(Discard, frm=player.library, card=card)
		
class ThroneRoom(Action):
	name = 'Throne Room'
	def __init__(self, session, **kwargs):
		super(ThroneRoom, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
		self.links = []
		self.connectCondition(Replacement, trigger='Destroy', source=self.card, resolve=self.resolveDestroy, condition=self.conditionDestroy)
		self.connectCondition(Replacement, trigger='MoveCard', source=self.card, resolve=self.resolveMoveLink, condition=self.conditionMoveLink)
	def onPlay(self, player, **kwargs):
		super(ThroneRoom, self).onPlay(player, **kwargs)
		self.links = []
		options = [o for o in player.hand if 'ACTION' in o.types]
		if not options: return
		choice = player.user([o.view() for o in options], 'Choose action')
		if not player.resolveEvent(CastCard, card=options[choice]): return
		self.links.append(options[choice])
		player.resolveEvent(PlayCard, card=options[choice])
	def conditionDestroy(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay
	def resolveDestroy(self, event, **kwargs):
		if event.card==self.card and self.links: return
		if event.card in self.links: self.links.remove(event.card)
		if not self.links: event.spawn(Destroy, card=self.card).resolve()
		return event.spawnClone().resolve()
	def conditionMoveLink(self, **kwargs):
		return self.owner and kwargs['player']==self.owner and kwargs['card'] in self.links and kwargs['frm']==self.owner.inPlay
	def resolveMoveLink(self, event, **kwargs):
		self.links.remove(event.card)
		return event.spawnClone().resolve()

class CouncilRoom(Action):
	name = 'Council Room'
	def __init__(self, session, **kwargs):
		super(CouncilRoom, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(CouncilRoom, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=4)
		player.resolveEvent(AddBuy)
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.resolveEvent(Draw)

class Festival(Action):
	name = 'Festival'
	def __init__(self, session, **kwargs):
		super(Festival, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Festival, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		player.resolveEvent(AddAction, amnt=2)
		player.resolveEvent(AddBuy)
		
class Laboratory(Action):
	name = 'Laboratory'
	def __init__(self, session, **kwargs):
		super(Laboratory, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Laboratory, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=2)
		player.resolveEvent(AddAction)
		
class Library(Action):
	name = 'Library'
	def __init__(self, session, **kwargs):
		super(Library, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Library, self).onPlay(player, **kwargs)
		aside = CPile()
		while len(player.hand)<7:
			card = player.resolveEvent(Draw)
			if not card: break
			if 'ACTION' in card.types and not player.user(('Yes', 'No'), 'Set aside '+card.view()):
				player.resolveEvent(Reveal, card=card)
				player.resolveEvent(MoveCard, frm=player.hand, to=aside, card=card)
		for card in copy.copy(aside): player.resolveEvent(Discard, frm=aside, card=card)

class Market(Action):
	name = 'Market'
	def __init__(self, session, **kwargs):
		super(Market, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Market, self).onPlay(player, **kwargs)
		player.resolveEvent(Draw)
		player.resolveEvent(AddAction)
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddBuy)

class Mine(Action):
	name = 'Mine'
	def __init__(self, session, **kwargs):
		super(Mine, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Mine, self).onPlay(player, **kwargs)
		options = [o for o in player.hand if 'TREASURE' in o.types]
		if not options: return
		choice = player.user([o.view() for o in options], 'Choose treasure trash')
		card = options[choice]
		player.resolveEvent(Trash, frm=player.hand, card=card)
		pile = player.pileCostingLess(4, card=card, restriction=lambda o: 'TREASURE' in o.types)
		if pile: player.resolveEvent(GainFromPile, frm=pile, to=player.hand)
		
class Witch(Action, Attack):
	name = 'Witch'
	def __init__(self, session, **kwargs):
		super(Witch, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Witch, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=2)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		player.resolveEvent(GainFromPile, frm=player.session.piles['Curse'])
		
class Adventurer(Action):
	name = 'Adventurer'
	def __init__(self, session, **kwargs):
		super(Adventurer, self).__init__(session, **kwargs)
		self.coinPrice.set(6)
	def onPlay(self, player, **kwargs):
		super(Adventurer, self).onPlay(player, **kwargs)
		aside = CPile()
		foundTreasure = CPile()
		while len(foundTreasure)<2:
			card = player.resolveEvent(RequestCard)
			if not card: break
			player.resolveEvent(Reveal, card=card)
			if 'TREASURE' in card.types: player.resolveEvent(MoveCard, frm=player.library, to=foundTreasure, card=card)
			else: player.resolveEvent(MoveCard, frm=player.library, to=aside, card=card)
		for card in copy.copy(foundTreasure): player.resolveEvent(MoveCard, frm=foundTreasure, to=player.hand, card=card)
		for card in copy.copy(aside): player.resolveEvent(Discard, frm=aside, card=card)

baseSet = [Cellar, Chapel, Moat, Chancellor, Village, Woodcutter, Workshop, Bureaucrat, Feast, Gardens, Militia, Remodel, Smithy, Spy, Thief, ThroneRoom, CouncilRoom, Festival, Laboratory, Library, Market, Mine, Witch, Adventurer]

class Loan(Treasure):
	name = 'Loan'
	def __init__(self, session, **kwargs):
		super(Loan, self).__init__(session, **kwargs)
		self.coinValue.set(1)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Loan, self).onPlay(player, **kwargs)
		aside = CPile()
		while True:
			card = player.resolveEvent(RequestCard)
			if not card: break
			player.resolveEvent(Reveal, card=card)
			if 'TREASURE' in card.types:
				if player.user(['discard', 'trash'], 'Choose '): player.resolveEvent(Trash, frm=player.library, card=card)
				else: player.resolveEvent(Discard, frm=player.library, card=card)
				break
			else: player.resolveEvent(MoveCard, frm=player.library, to=aside, card=card)
		for card in copy.copy(aside): player.resolveEvent(Discard, frm=aside, card=card)

class TradeToken(Token):
	name = 'TradeToken'
	def __init__(self, session, **kwargs):
		super(TradeToken, self).__init__(session, **kwargs)
		self.session.connectCondition(DelayedTrigger, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
	def conditionGain(self, **kwargs):
		return kwargs['frm']==self.owner
	def resolveGain(self, **kwargs):
		kwargs['player'].resolveEvent(MoveToken, frm=self.owner.tokens, to=self.session.globalMats['TradeRouteMat'], token=self)
		
class TradeRoute(Action):
	name = 'Trade Route'
	class TradeRouteSetup(DelayedTrigger):
		name = 'TradeRouteSetup'
		defaultTrigger = 'globalSetup'
		def resolve(self, **kwargs):
			for pile in self.source.session.piles:
				if 'VICTORY' in self.source.session.piles[pile].maskot.types: self.source.session.resolveEvent(AddToken, to=self.source.session.piles[pile], token=TradeToken(self.source.session))
	def __init__(self, session, **kwargs):
		super(TradeRoute, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(TradeRoute, self).onPlay(player, **kwargs)
		player.resolveEvent(AddBuy)
		player.resolveEvent(AddCoin, amnt=len(self.session.globalMats['TradeRouteMat']))
		card = player.selectCard(message='Choose trash')
		if card: player.resolveEvent(Trash, frm=player.hand, card=card)
	def onPileCreate(self, pile, session, **kwargs):
		super(TradeRoute, self).onPileCreate(pile, session, **kwargs)
		session.addGlobalMat('TradeRouteMat')
		self.session.connectCondition(self.TradeRouteSetup, source=self)
		
class Watchtower(Action, Reaction):
	name = 'Watchtower'
	def __init__(self, session, **kwargs):
		super(Watchtower, self).__init__(session, **kwargs)
		Reaction.__init__(self, session, **kwargs)
		self.coinPrice.set(3)
		self.connectCondition(Replacement, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
	def onPlay(self, player, **kwargs):
		super(Watchtower, self).onPlay(player, **kwargs)
		while len(player.hand)<6 and player.resolveEvent(Draw): pass
	def conditionGain(self, **kwargs):
		return self.owner and kwargs['player']==self.owner and self.card in self.owner.hand
	def resolveGain(self, event, **kwargs):
		choice = self.owner.user(('no', 'trash', 'top'), 'Choose mode for '+event.card.view())
		if choice==0: return event.spawnClone().resolve()
		elif choice==1:
			event.spawnClone().resolve()
			self.owner.resolveEvent(Reveal, card=self.card)
			return event.spawn(Trash, frm=event.to).resolve()
		else:
			self.owner.resolveEvent(Reveal, card=self.card)
			return event.spawnClone(to=self.owner.library).resolve()
		
class Bishop(Action):
	name = 'Bishop'
	def __init__(self, session, **kwargs):
		super(Bishop, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Bishop, self).onPlay(player, **kwargs)		
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddVictory)
		card = player.selectCard(message='Choose trash')
		if card:
			player.resolveEvent(AddVictory, amnt=m.floor(card.coinPrice.access()/2))
			player.resolveEvent(Trash, frm=player.hand, card=card)
		for aplayer in self.session.getOtherPlayers(player):
			card = aplayer.selectCard(message='Choose trash', optional=True)
			if card: aplayer.resolveEvent(Trash, frm=aplayer.hand, card=card)
		
class Monument(Action):
	name = 'Monument'
	def __init__(self, session, **kwargs):
		super(Monument, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Monument, self).onPlay(player, **kwargs)
		player.resolveEvent(AddVictory)
		player.resolveEvent(AddCoin, amnt=2)

class Quarry(Treasure):
	name = 'Quarry'
	def __init__(self, session, **kwargs):
		super(Quarry, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
		self.coinValue.set(1)
		self.connectCondition(ADStatic, trigger='coinPrice', source=self, resolve=self.resolveAccess, condition=self.conditionAccess)
	def conditionAccess(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay and hasattr(kwargs['master'], 'types') and 'ACTION' in kwargs['master'].types
	def resolveAccess(self, val, **kwargs):
		if val<2: return 0
		return val-2

class Talisman(Treasure):
	name = 'Talisman'
	def __init__(self, session, **kwargs):
		super(Talisman, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
		self.coinValue.set(1)
		self.connectCondition(Trigger, trigger='Buy', source=self, resolve=self.resolveBuy, condition=self.conditionBuy)
	def conditionBuy(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay and kwargs['card'].coinPrice.access()<5
	def resolveBuy(self, **kwargs):
		self.owner.resolveEvent(GainFromPile, frm=kwargs['card'].frmPile)
	
class WorkersVillage(Action):
	name = "Worker's Village"
	def __init__(self, session, **kwargs):
		super(WorkersVillage, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(WorkersVillage, self).onPlay(player, **kwargs)	
		player.resolveEvent(AddAction, amnt=2)
		player.resolveEvent(Draw)
		player.resolveEvent(AddBuy)
		
class City(Action):
	name = 'City'
	def __init__(self, session, **kwargs):
		super(City, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(City, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction, amnt=2)
		empty = len(self.session.getEmptyPiles())
		if empty>0:
			player.resolveEvent(DrawCards, amnt=2)
			if empty>1:
				player.resolveEvent(AddCoin)
				player.resolveEvent(AddBuy)
		else: player.resolveEvent(Draw)

class Contraband(Treasure):
	name = 'Contraband'
	class ContrabandBan(ReplaceThisTurn):
		name = 'ContrabandBan'
		defaultTrigger = 'Purchase'
		def condition(self, **kwargs):
			return kwargs['card'].frmPile==self.banning
		def resolve(self, event, **kwargs):
			return
	def __init__(self, session, **kwargs):
		super(Contraband, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		self.coinValue.set(3)
	def onPlay(self, player, **kwargs):
		super(Contraband, self).onPlay(player, **kwargs)
		player.resolveEvent(AddBuy)
		pile = self.session.getNextPlayer(player).getPile()
		self.session.connectCondition(self.ContrabandBan, source=self, banning=pile)
	
class CountingHouse(Action):
	name = 'Counting House'
	def __init__(self, session, **kwargs):
		super(CountingHouse, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(CountingHouse, self).onPlay(player, **kwargs)
		coppers = [o for o in player.discardPile if o.name=='Copper']
		for i in range(player.user(list(range(len(coppers)+1)), 'Choose amount')):
			player.resolveEvent(Reveal, card=coppers[i])
			player.resolveEvent(MoveCard, frm=player.discardPile, to=player.hand, card=coppers[i])

class Mint(Action):
	name = 'Mint'
	def __init__(self, session, **kwargs):
		super(Mint, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		self.connectCondition(Trigger, trigger='Buy', source=self, resolve=self.resolveBuy, condition=self.conditionBuy)
	def onPlay(self, player, **kwargs):
		super(Mint, self).onPlay(player, **kwargs)
		card = player.selectCard(message='Choose gain', restriction=lambda o: 'TREASURE' in o.types)
		if card and card.name in self.session.piles:
			player.resolveEvent(Reveal, card=card)
			player.resolveEvent(GainFromPile, frm=self.session.piles[card.name])
	def conditionBuy(self, **kwargs):
		return kwargs['card']==self.card
	def resolveBuy(self, **kwargs):
		for card in copy.copy(kwargs['player'].inPlay):
			if 'TREASURE' in card.types: kwargs['player'].resolveEvent(Trash, frm=kwargs['player'].inPlay, card=card)
	
class Mountebank(Action, Attack):
	name = 'Mountebank'
	def __init__(self, session, **kwargs):
		super(Mountebank, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Mountebank, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		for i in range(len(player.hand)):
			if player.hand[i].name=='Curse':
				if player.user(('keep', 'discardCurse'), ''):
					player.resolveEvent(Discard, card=player.hand[i])
					return
				break
		player.resolveEvent(GainFromPile, frm=self.session.piles['Curse'])
		player.resolveEvent(GainFromPile, frm=self.session.piles['Copper'])

class Rabble(Action, Attack):
	name = 'Rabble'
	def __init__(self, session, **kwargs):
		super(Rabble, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Rabble, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=3)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		cards = player.resolveEvent(RequestCards, amnt=3)
		for card in cards:
			if 'ACTION' in cards.types or 'TREASURE' in card.types: player.resolveEvent(Discard, frm=player.library, card=card)

class Vault(Action):
	name = 'Vault'
	def __init__(self, session, **kwargs):
		super(Vault, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Vault, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=2)
		cards = player.selectCards(optional=True, message='Choose discard')
		for card in cards: player.resolveEvent(Discard, frm=player.hand, card=card)
		player.resolveEvent(AddCoin, amnt=len(cards))
		for aplayer in self.session.getOtherPlayers(player):
			if len(aplayer.hand)>1 and aplayer.user(('discard', 'DoNotDiscard'), ''):
				cards = aplayer.selectCards(2, message='Choose discard')
				if len(cards)>1:
					for card in cards: aplayer.resolveEvent(Discard, card=card)
					aplayer.resolveEvent(Draw)

class Venture(Treasure):
	name = 'Venture'
	def __init__(self, session, **kwargs):
		super(Venture, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		self.coinValue.set(1)
	def onPlay(self, player, **kwargs):
		super(Venture, self).onPlay(player, **kwargs)
		aside = CPile()
		while True:
			card = player.resolveEvent(RequestCard)
			if not card: break
			player.resolveEvent(Reveal, card=card)
			if 'TREASURE' in card.types:
				player.resolveEvent(CastCard, frm=player.library, card=card)
				break
			else: player.resolveEvent(MoveCard, frm=player.library, to=aside, card=card)
		for card in copy.copy(aside): player.resolveEvent(Discard, frm=aside, card=card)

class Goons(Action, Attack):
	name = 'Goons'
	def __init__(self, session, **kwargs):
		super(Goons, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(6)
		self.connectCondition(Trigger, trigger='Buy', source=self, resolve=self.resolveBuy, condition=self.conditionBuy)
	def onPlay(self, player, **kwargs):
		super(Goons, self).onPlay(player, **kwargs)
		player.resolveEvent(AddBuy)
		player.resolveEvent(AddCoin, amnt=2)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		while len(player.hand)>3: player.resolveEvent(Discard, card=player.selectCard(message='Choose discard'))
	def conditionBuy(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay
	def resolveBuy(self, **kwargs):
		self.owner.resolveEvent(AddVictory)

class GrandMarket(Action):
	name = 'Grand Market'
	def __init__(self, session, **kwargs):
		super(GrandMarket, self).__init__(session, **kwargs)
		self.coinPrice.set(6)
		self.connectCondition(Replacement, trigger='Purchase', source=self, resolve=self.resolvePurchase, condition=self.conditionPurchase)
	def onPlay(self, player, **kwargs):
		super(GrandMarket, self).onPlay(player, **kwargs)
		player.resolveEvent(AddBuy)
		player.resolveEvent(Draw)
		player.resolveEvent(AddAction)
		player.resolveEvent(AddCoin, amnt=2)
	def conditionPurchase(self, **kwargs):
		return kwargs['card']==self.card and 'Copper' in [o.name for o in kwargs['player'].inPlay]
	def resolvePurchase(self, event, **kwargs):
		return

class Hoard(Treasure):
	name = 'Hoard'
	def __init__(self, session, **kwargs):
		super(Hoard, self).__init__(session, **kwargs)
		self.coinPrice.set(6)
		self.coinValue.set(2)
		self.connectCondition(Trigger, trigger='Buy', source=self, resolve=self.resolveBuy, condition=self.conditionBuy)
	def conditionBuy(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay and 'VICTORY' in kwargs['card'].types
	def resolveBuy(self, **kwargs):
		self.owner.resolveEvent(GainFromPile, frm=self.session.piles['Gold'])
	
class Bank(Treasure):
	name = 'Bank'
	def __init__(self, session, **kwargs):
		super(Bank, self).__init__(session, **kwargs)
		self.coinPrice.set(7)
	def onPlay(self, player, **kwargs):
		player.resolveEvent(AddCoin, amnt=len([o for o in player.inPlay if 'TREASURE' in o.types]))

class Expand(Action):
	name = 'Expand'
	def __init__(self, session, **kwargs):
		super(Expand, self).__init__(session, **kwargs)
		self.coinPrice.set(7)
	def onPlay(self, player, **kwargs):
		super(Expand, self).onPlay(player, **kwargs)
		card = player.selectCard(message='Choose trash')
		if not card: return
		player.resolveEvent(Trash, card=card, frm=player.hand)
		player.gainCostingLessThan(4, card=card)
	
class Forge(Action):
	name = 'Forge'
	def __init__(self, session, **kwargs):
		super(Forge, self).__init__(session, **kwargs)
		self.coinPrice.set(7)
	def onPlay(self, player, **kwargs):
		super(Forge, self).onPlay(player, **kwargs)
		cards = selectCards(optional=True, message='Choose trash')
		if not cards: return
		for card in cards: player.resolveEvent(Trash, frm=player.hand, card=card)
		player.gainCosting(np.sum([o.coinPrice.access() for o in cards]))

class KingsCourt(Action):
	name = "King's Court"
	def __init__(self, session, **kwargs):
		super(KingsCourt, self).__init__(session, **kwargs)
		self.coinPrice.set(7)
		self.links = []
		self.connectCondition(Replacement, trigger='Destroy', source=self.card, resolve=self.resolveDestroy, condition=self.conditionDestroy)
		self.connectCondition(Replacement, trigger='MoveCard', source=self.card, resolve=self.resolveMoveLink, condition=self.conditionMoveLink)
	def onPlay(self, player, **kwargs):
		super(KingsCourt, self).onPlay(player, **kwargs)
		self.links = []
		options = [o for o in player.hand if 'ACTION' in o.types]
		if not options: return
		choice = player.user([o.view() for o in options], 'Choose action')
		if not player.resolveEvent(CastCard, card=options[choice]): return
		self.links.append(options[choice])
		for i in range(2): player.resolveEvent(PlayCard, card=options[choice])
	def conditionDestroy(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay
	def resolveDestroy(self, event, **kwargs):
		if event.card==self.card and self.links: return
		if event.card in self.links: self.links.remove(event.card)
		if not self.links: event.spawn(Destroy, card=self.card).resolve()
		return event.spawnClone().resolve()
	def conditionMoveLink(self, **kwargs):
		return self.owner and kwargs['player']==self.owner and kwargs['card'] in self.links and kwargs['frm']==self.owner.inPlay
	def resolveMoveLink(self, event, **kwargs):
		self.links.remove(event.card)
		return event.spawnClone().resolve()
	
class Peddler(Action):
	name = 'Peddler'
	def __init__(self, session, **kwargs):
		super(Peddler, self).__init__(session, **kwargs)
		self.coinPrice.set(8)
		self.connectCondition(ADStatic, trigger='coinPrice', source=self, resolve=self.resolveAccess, condition=self.conditionAccess)
	def onPlay(self, player, **kwargs):
		super(Peddler, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddAction)
		player.resolveEvent(Draw)
	def conditionAccess(self, **kwargs):	
		if not kwargs['master']==self: return False
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='actionPhase' or self.session.events[i][0]=='treasurePhase': return False
			elif self.session.events[i][0]=='buyPhase': return True
	def resolveAccess(self, val, **kwargs):
		v = val-len([o for o in self.session.activePlayer.inPlay if 'ACTION' in o.types])*2
		if v>0: return v
		return 0
	
prosperity = [Loan, TradeRoute, Watchtower, Bishop, Monument, Quarry, Talisman, WorkersVillage, City, Contraband, CountingHouse, Mint, Mountebank, Rabble, Vault, Venture, Goons, GrandMarket, Hoard, Expand, KingsCourt, Peddler]
			
class EmbargoToken(Token):
	name = 'Embargo Token'
	def __init__(self, session, **kwargs):
		super(EmbargoToken, self).__init__(session, **kwargs)
		session.connectCondition(Replacement, trigger='Buy', source=self, resolve=self.resolveBuy, condition=self.conditionBuy)
	def conditionBuy(self, **kwargs):
		return self.owner and kwargs['frm']==self.owner
	def resolveBuy(self, event, **kwargs):
		kwargs['player'].resolveEvent(GainFromPile, frm=self.owner.session.piles['Curse'])
		return event.spawnClone.resolve()
		
class Embargo(Action):
	name = 'Embargo'
	def __init__(self, session, **kwargs):
		super(Embargo, self).__init__(session, **kwargs)
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(Embargo, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		player.resolveEvent(Trash, frm=player.inPlay, card=self.card)
		player.resolveEvent(AddToken, to=player.session.piles[list(player.session.piles)[player.user(list(player.session.piles), 'Choose embargo')]], token=EmbargoToken(player.session))
		
class Haven(Action, Duration):
	name = 'Haven'
	def __init__(self, session, **kwargs):
		super(Haven, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(2)
		self.saved = CPile()
	def onPlay(self, player, **kwargs):
		super(Haven, self).onPlay(player, **kwargs)
		Duration.onPlay(self, player, **kwargs)
		player.resolveEvent(Draw)
		player.resolveEvent(AddAction)
		card = player.selectCard(message='Choose saved')
		if not card: return
		card = player.resolveEvent(MoveCard, frm=player.hand, to=player.mats['HavenMat'], card=card)
		if card: self.saved.append(card)
	def duration(self, **kwargs):
		while self.saved: self.owner.resolveEvent(MoveCard, frm=self.owner.mats['HavenMat'], to=self.owner.hand, card=self.saved.pop())
	def onPileCreate(self, pile, session, **kwargs):
		super(Haven, self).onPileCreate(pile, session, **kwargs)
		session.addMat('HavenMat', private=True)

class Lighthouse(Action, Duration):
	name = 'Lighthouse'
	class LighthouseProtect(DelayedReplacement):
		name = 'LighthouseProtect'
		defaultTrigger = 'ResolveAttack'
		def condition(self, **kwargs):
			return kwargs['source']==self.enemy
	def __init__(self, session, **kwargs):
		super(Lighthouse, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(2)
		self.connectCondition(Replacement, trigger='PlayCard', source=self.card, resolve=self.resolveReact, condition=self.conditionReact)
	def onPlay(self, player, **kwargs):
		super(Lighthouse, self).onPlay(player, **kwargs)
		Duration.onPlay(self, player, **kwargs)
		player.resolveEvent(AddAction)
		player.resolveEvent(AddCoin)
	def duration(self, **kwargs):
		self.owner.resolveEvent(AddCoin)
	def conditionReact(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay and 'ATTACK' in kwargs['card'].types and self.owner!=kwargs['player']
	def resolveReact(self, event, **kwargs):
		self.session.connectCondition(self.LighthouseProtect, source=self.card, enemy=event.card)
		return event.spawnClone().resolve()
		
class NativeVillage(Action):
	name = 'Native Village'
	def __init__(self, session, **kwargs):
		super(NativeVillage, self).__init__(session, **kwargs)
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(NativeVillage, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction, amnt=2)
		if player.user(('takeCards', 'addCard'), 'Choose mode'):
			topCard = player.resolveEvent(RequestCard)
			if topCard: player.resolveEvent(MoveCard, frm=player.library, to=player.mats['NativeVillageMat'], card=topCard)
		else:
			for card in copy.copy(player.mats['NativeVillageMat']): player.resolveEvent(MoveCard, frm=player.mats['NativeVillageMat'], to=player.hand, card=card)
	def onPileCreate(self, pile, session, **kwargs):
		super(NativeVillage, self).onPileCreate(pile, session, **kwargs)
		session.addMat('NativeVillageMat', private=True)

class PearlDiver(Action):
	name = 'Pearl Diver'
	def __init__(self, session, **kwargs):
		super(PearlDiver, self).__init__(session, **kwargs)
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(PearlDiver, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction)
		player.resolveEvent(Draw)
		if not player.library: return
		card = player.library[0]
		player.resolveEvent(Reveal, card=card, hidden=player)
		if not player.user(('top', 'bot'), ''):
			player.resolveEvent(Message, content='Pearl Diver top')
			player.resolveEvent(MoveCard, frm=player.library, to=player.library, card=card)

class Ambassador(Action, Attack):
	name = 'Ambassador'
	def __init__(self, session, **kwargs):
		super(Ambassador, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Ambassador, self).onPlay(player, **kwargs)
		revealedCard = player.selectCard(message='Choose return')
		if not revealedCard: return
		player.resolveEvent(Reveal, card=revealedCard)
		if not revealedCard.name in player.session.piles: return
		amnt = player.user(list(range(3)), 'Choose return amount')
		returned = 0
		for card in copy.copy(player.hand):
			if returned==amnt: break
			if card.name==revealedCard.name:
				player.resolveEvent(ReturnCard, card=card, frm=player.hand)
				returned+=1
			break
		if card.frmPile.name in self.session.piles:	self.attackOpponents(player, pile=card.frmPile)
	def attack(self, player, **kwargs):
		player.resolveEvent(GainFromPile, frm=kwargs['pile'])

class FishingVillage(Action, Duration):
	name = 'Fishing Village'
	def __init__(self, session, **kwargs):
		super(FishingVillage, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(FishingVillage, self).onPlay(player, **kwargs)
		Duration.onPlay(self, player, **kwargs)
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddAction, amnt=2)
	def duration(self, **kwargs):
		self.owner.resolveEvent(AddCoin)
		self.owner.resolveEvent(AddAction)

class Lookout(Action):
	name = 'Lookout'
	def __init__(self, session, **kwargs):
		super(Lookout, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Lookout, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction)
		cards = player.resolveEvent(RequestCards, amnt=3)
		if not cards: return
		player.resolveEvent(Trash, frm=player.library, card=cards.pop(player.user([o.view() for o in cards], 'Choose trash')))
		if not cards: return
		player.resolveEvent(Discard, frm=player.library, card=cards.pop(player.user([o.view() for o in cards], 'Choose discard')))
		
class Smugglers(Action):
	name = 'Smugglers'
	def __init__(self, session, **kwargs):
		super(Smugglers, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Smugglers, self).onPlay(player, **kwargs)
		previousPlayer = player.session.getPreviousPlayer(player)
		options = []
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='startTurn' and player.session.events[i][1]['player']==previousPlayer:
				for n in range(i, len(player.session.events)):
					if player.session.events[n][0]=='Gain' and player.session.events[n][1]['player']==previousPlayer and player.session.events[n][1]['card'].getPrice(player)<7: options.append(player.session.events[n][1]['card'].name)
					elif player.session.events[n][0]=='endTurn': break
				break
		if not options: return
		player.resolveEvent(GainFromPile, frm=self.session.piles[options[player.user(options, 'Choose smuggle')]])
		
class Warehouse(Action):
	name = 'Warehouse'
	def __init__(self, session, **kwargs):
		super(Warehouse, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Warehouse, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction)
		player.resolveEvent(DrawCards, amnt=3)
		for card in player.selectCards(3): player.resolveEvent(Discard, card=card)
		
class Caravan(Action, Duration):
	name = 'Caravan'
	def __init__(self, session, **kwargs):
		super(Caravan, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Caravan, self).onPlay(player, **kwargs)
		Duration.onPlay(self, player, **kwargs)
		player.resolveEvent(AddAction)
		player.resolveEvent(Draw)
	def duration(self, **kwargs):
		self.owner.resolveEvent(Draw)
		
class Cutpurse(Action, Attack):
	name = 'Cutpurse'
	def __init__(self, session, **kwargs):
		super(Cutpurse, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Cutpurse, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		for i in range(len(player.hand)):
			if player.hand[i].name=='Copper':
				player.resolveEvent(Discard, card=player.hand[i])
				return
		for card in player.hand: player.resolveEvent(Reveal, card=card)
		
class Island(Action, Victory):
	name = 'Island'
	def __init__(self, session, **kwargs):
		super(Island, self).__init__(session, **kwargs)
		Victory.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
		self.victoryValue.set(2)
	def onPlay(self, player, **kwargs):
		super(Island, self).onPlay(player, **kwargs)
		card = player.selectCard(message='Choose hide')
		if card: player.resolveEvent(MoveCard, frm=player.hand, to=player.mats['IslandMat'], card=card)
		player.resolveEvent(MoveCard, frm=player.inPlay, to=player.mats['IslandMat'], card=self.card)
	def onPileCreate(self, pile, session, **kwargs):
		super(Island, self).onPileCreate(pile, session, **kwargs)
		session.addMat('IslandMat')

class Navigator(Action):
	name = 'Navigator'
	def __init__(self, session, **kwargs):
		super(Navigator, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Navigator, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		cards = player.resolveEvent(RequestCards, amnt=5)
		if not cards: return
		for card in cards: player.resolveEvent(Reveal, card=card, hidden=player)
		if player.user(('top', 'discard'), 'Choose navigator mode'):
			for card in copy.copy(cards): player.resolveEvent(Discard, frm=player.library, card=card)
		else:
			while cards: player.resolveEvent(MoveCard, frm=player.library, to=player.library, card=cards.pop(player.user([o.view() for o in cards], 'Choose top order')))

class PirateToken(Token): pass
		
class PirateShip(Action, Attack):
	name = 'Pirate Ship'
	def __init__(self, session, **kwargs):
		super(PirateShip, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(PirateShip, self).onPlay(player, **kwargs)
		if player.user(('attack', 'money'), ''): player.resolveEvent(AddCoin, amnt=len(player.mats['PirateMat']))
		else:
			if True in self.attackOpponents(player): player.resolveEvent(AddToken, to=player.mats['PirateMat'], token=PirateToken())
	def onPileCreate(self, pile, session, **kwargs):
		super(PirateShip, self).onPileCreate(pile, session, **kwargs)
		session.addMat('PirateMat')
	def attack(self, player, **kwargs):
		cards = player.resolveEvent(RequestCards, amnt=2)
		if not cards: return
		hit = False
		options = [o for o in cards if 'VICTORY' in o.types]
		if options:
			choice = self.owner.user([o.view() for o in options], 'Choose trash')
			if player.resolveEvent(Trash, frm=player.library, card=cards.pop(cards.index(options[choice]))): hit = True
		for card in cards: player.resolveEvent(Discard, frm=player.library, card=card)
		return hit
		
class Salvager(Action):
	name = 'Salvager'
	def __init__(self, session, **kwargs):
		super(Salvager, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Salvager, self).onPlay(player, **kwargs)
		player.resolveEvent(AddBuy)
		card = player.selectCard(message='Choose trash')
		if not card: return
		player.resolveEvent(AddCoin, amnt=card.coinPrice.access())
		player.resolveEvent(Trash, frm=player.hand, card=card)

class SeaHag(Action, Attack):
	name = 'Sea Hag'
	def __init__(self, session, **kwargs):
		super(SeaHag, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(SeaHag, self).onPlay(player, **kwargs)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		card = player.resolveEvent(RequestCard)
		if card: player.resolveEvent(Discard, frm=player.library, card=card)
		player.resolveEvent(GainFromPile, frm=self.session.piles['Curse'], to=player.library)

class TreasureMap(Action):
	name = 'Treasure Map'
	def __init__(self, session, **kwargs):
		super(TreasureMap, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(TreasureMap, self).onPlay(player, **kwargs)
		player.resolveEvent(Trash, frm=player.inPlay, card=self.card)
		for i in range(len(player.hand)):
			if player.hand[i].name=='Treasure Map':
				if not player.resolveEvent(Trash, frm=player.hand, card=player.hand[i]): return
				for n in range(4): player.resolveEvent(GainFromPile, frm=self.session.piles['Gold'], to=player.library)
				return

class Bazaar(Action):
	name = 'Bazaar'
	def __init__(self, session, **kwargs):
		super(Bazaar, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Bazaar, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction, amnt=2)
		player.resolveEvent(Draw)
		player.resolveEvent(AddCoin)

class Explorer(Action):
	name = 'Explorer'
	def __init__(self, session, **kwargs):
		super(Explorer, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Explorer, self).onPlay(player, **kwargs)
		provinces = [o for o in player.hand if o.name=='Province']
		if provinces and player.user(('no', 'yes'), 'Reveal Province'):
			player.resolveEvent(Reveal, card=provinces[0])
			player.resolveEvent(GainFromPile, frm=self.session.piles['Gold'], to=player.hand)
		else: player.resolveEvent(GainFromPile, frm=self.session.piles['Silver'], to=player.hand)

class GhostShip(Action, Attack):
	name = 'Ghost Ship'
	def __init__(self, session, **kwargs):
		super(GhostShip, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(GhostShip, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=2)
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		while len(player.hand)>3:
			player.resolveEvent(MoveCard, frm=player.hand, to=player.library, card=player.selectCard(message='Choose top'))

class MerchantShip(Action, Duration):
	name = 'Merchant Ship'
	def __init__(self, session, **kwargs):
		super(MerchantShip, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(MerchantShip, self).onPlay(player, **kwargs)
		Duration.onPlay(self, player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
	def duration(self, **kwargs):
		self.owner.resolveEvent(AddCoin, amnt=2)

class Outpost(Action, Duration):
	name = 'Outpost'
	def __init__(self, session, **kwargs):
		super(Outpost, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Outpost, self).onPlay(player, **kwargs)
		player.eotdraw = 3
		player.session.extraTurns.append((self.outpostTurn, {'player': player}))
	def outpostTurn(self, **kwargs):
		turns = 0
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[0]=='startTurn':
				if self.session.event[1]['player']==self: turns+=1
				else: break
		if turns>1: return
		self.session.activePlayer = kwargs['player']
		self.session.turnFlag = 'outpost'
		kwargs['player'].resetValues()
		self.session.dp.send(signal='startTurn', player=kwargs['player'], flags=self.session.turnFlag)
		kwargs['player'].session.resolveTriggerQueue()
		kwargs['player'].actionPhase()
		kwargs['player'].treasurePhase()
		kwargs['player'].buyPhase()
		kwargs['player'].endTurn()
		
class Tactician(Action, Duration):
	name = 'Tactician'
	def __init__(self, session, **kwargs):
		super(Tactician, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Tactician, self).onPlay(player, **kwargs)
		if not player.hand: return
		player.discardHand()
		self.session.connectCondition(self.DurationTrigger, source=self.card)
	def duration(self, **kwargs):
		self.owner.resolveEvent(DrawCards, amnt=5)
		self.owner.resolveEvent(AddBuy)
		self.owner.resolveEvent(AddAction)

class Treasury(Action):
	name = 'Treasury'
	def __init__(self, session, **kwargs):
		super(Treasury, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		self.connectCondition(Trigger, trigger='endTurn', source=self.card, resolve=self.resolveEndTurn, condition=self.conditionEndTurn)
	def onPlay(self, player, **kwargs):
		super(Treasury, self).onPlay(player, **kwargs)
		player.resolveEvent(Draw)
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddAction)
	def conditionEndTurn(self, **kwargs):
		if not (self.owner and kwargs['player']==self.owner and self.card in self.owner.inPlay): return False
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='Buy' and self.session.events[i][1]['card'] and 'VICTORY' in self.session.events[i][1]['card'].types: return
			elif self.session.events[i][0]=='startTurn': break
		return True
	def resolveEndTurn(self, **kwargs):
		if player.user(('discard', 'top'), 'Treasury'): self.owner.resolveEvent(MoveCard, frm=self.owner.inPlay, to=self.owner.library, card=self.card)
	
class Wharf(Action, Duration):
	name = 'Wharf'
	def __init__(self, session, **kwargs):
		super(Wharf, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Wharf, self).onPlay(player, **kwargs)
		Duration.onPlay(self, player, **kwargs)
		player.resolveEvent(DrawCards, amnt=2)
		player.resolveEvent(AddBuy)
	def duration(self, **kwargs):
		self.owner.resolveEvent(DrawCards, amnt=2)
		self.owner.resolveEvent(AddBuy)
		
seaside = [Embargo, Haven, Lighthouse, NativeVillage, PearlDiver, Ambassador, FishingVillage, Lookout, Smugglers, Caravan, Cutpurse, Island, Navigator, PirateShip, Salvager, SeaHag, TreasureMap, Bazaar, Explorer, GhostShip, MerchantShip, Outpost, Tactician, Treasury, Wharf]

class Fortress(Action):
	name = 'Fortress'
	def __init__(self, session, **kwargs):
		super(Fortress, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
		self.connectCondition(Replacement, trigger='Trash', source=self.card, resolve=self.resolveTrash, condition=self.conditionTrash)
	def onPlay(self, player, **kwargs):
		super(Fortress, self).onPlay(player, **kwargs)
		player.resolveEvent(Draw)
		player.resolveEvent(AddAction, amnt=2)
	def conditionTrash(self, **kwargs):
		return kwargs['card']==self.card
	def resolveTrash(self, event, **kwargs):
		trashedCard = event.spawnClone().resolve()
		card =  event.player.resolveEvent(MoveCard, frm=self.session.trash, to=event.player.hand, card=self.card)
		if card: player.resolveEvent(GainOwnership, card=card)
		return trashedCard
	
class Procession(Action):
	name = 'Procession'
	def __init__(self, session, **kwargs):
		super(Procession, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
		self.links = []
		self.connectCondition(Replacement, trigger='Destroy', source=self.card, resolve=self.resolveDestroy, condition=self.conditionDestroy)
		self.connectCondition(Replacement, trigger='MoveCard', source=self.card, resolve=self.resolveMoveLink, condition=self.conditionMoveLink)
	def onPlay(self, player, **kwargs):
		super(Procession, self).onPlay(player, **kwargs)
		self.links = []
		options = [o for o in player.hand if 'ACTION' in o.types]
		if not options: return
		card =  options[player.user([o.view() for o in options], 'Choose action')]
		if not player.resolveEvent(CastCard, card=card): return
		self.links.append(card)
		player.resolveEvent(PlayCard, card=card)
		player.resolveEvent(Trash, frm=player.inPlay, card=card)
		player.gainCosting(1, card=card, restriction=lambda o: 'ACTION' in o.types)
	def conditionDestroy(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay
	def resolveDestroy(self, event, **kwargs):
		if event.card==self.card and self.links: return
		if event.card in self.links: self.links.remove(event.card)
		if not self.links: event.spawn(Destroy, card=self.card).resolve()
		return event.spawnClone().resolve()
	def conditionMoveLink(self, **kwargs):
		return self.owner and kwargs['player']==self.owner and kwargs['card'] in self.links and kwargs['frm']==self.owner.inPlay
	def resolveMoveLink(self, event, **kwargs):
		self.links.remove(event.card)
		return event.spawnClone().resolve()
	
class BandOfMisfits(Action):
	name = 'Band of Misfits'
	def __init__(self, session, **kwargs):
		super(BandOfMisfits, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		self.connectCondition(Replacement, trigger='CastCard', source=self.card, resolve=self.resolveCast, condition=self.conditionCast)
	def conditionMove(self, **kwargs):
		return kwargs['card']==self.card and kwargs['frm']==self.owner.inPlay and kwargs['to']!=self.owner.inPlay
	def resolveMove(self, event, **kwargs):
		self.card.disconnect()
		self.card.currentValues = BandOfMisfits(self.session, card=self.card)
		#self.owner.resolveEvent(GainOwnership, card=self.card)
		return event.spawnClone().resolve()
	def conditionCast(self, **kwargs):
		return kwargs['card']==self.card
	def resolveCast(self, event, **kwargs):
		pile = self.owner.pileCostingLess(card=self.card, restriction = lambda o: 'ACTION' in o.types)
		if not pile: return event.spawnClone().resolve()
		self.disconnect()
		self.card.currentValues = type(pile.viewTop().currentValues)(self.session, card=self.card)
		#self.owner.resolveEvent(GainOwnership, card=self.card)
		self.card.connectCondition(Replacement, trigger='MoveCard', source=self.card, resolve=self.resolveMove, condition=self.conditionMove)
		self.card.currentValues.view = self.view
		return event.spawnClone().resolve()
	def view(self, **kwargs):
		if not self.card.name==BandOfMisfits.name: return BandOfMisfits.name+'('+self.card.name+')'
		return self.card.name
		
darkages = [Fortress, Procession, BandOfMisfits]

class BoonToken(Token):
	name = 'Base Boon Token'
	def __init__(self, session, **kwargs):
		super(BoonToken, self).__init__(session, **kwargs)
		self.types.append('BOONTOKEN')
		session.connectCondition(Replacement, trigger='ResolveCard', source=self, resolve=self.resolvePlay, condition=self.conditionPlay)
	def conditionPlay(self, **kwargs):
		return self.owner and kwargs['player']==self.playerOwner and kwargs['card'].frmPile==self.owner
	def resolvePlay(self, event, **kwargs):
		self.boon()
		return event.spawnClone().resolve()
	def boon(self, **kwargs):
		pass

class PlusCard(BoonToken):
	name = 'Plus Card Token'
	def boon(self, **kwargs):
		self.playerOwner.resolveEvent(Draw)
		
class PlusAction(BoonToken):
	name = 'Plus Action Token'
	def boon(self, **kwargs):
		self.playerOwner.resolveEvent(AddAction)
		
class PlusBuy(BoonToken):
	name = 'Plus Buy Token'
	def boon(self, **kwargs):
		self.playerOwner.resolveEvent(AddBuy)
		
class PlusCoin(BoonToken):
	name = 'Plus Coin Token'
	def boon(self, **kwargs):
		self.playerOwner.resolveEvent(AddCoin)
		
class CoinOfTheRealm(Treasure, Reserve):
	name = 'Coin of the Realm'
	def __init__(self, session, **kwargs):
		super(CoinOfTheRealm, self).__init__(session, **kwargs)
		self.triggerSignal = 'PlayCard'
		Reserve.__init__(self, session, **kwargs)
		self.coinValue.set(1)
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(CoinOfTheRealm, self).onPlay(player, **kwargs)
		Reserve.onPlay(self, player, **kwargs)
	def call(self, **kwargs):
		self.owner.resolveEvent(AddAction, amnt=2)
	def onPileCreate(self, pile, session, **kwargs):
		super(CoinOfTheRealm, self).onPileCreate(pile, session, **kwargs)
		Reserve.onPileCreate(self, pile, session, **kwargs)
		
class Page(Action, Traveler):
	name = 'Page'
	def __init__(self, session, **kwargs):
		super(Page, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = TreasureHunter 
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(Page, self).onPlay(player, **kwargs)
		player.resolveEvent(Draw)
		player.resolveEvent(AddAction)
	def onPileCreate(self, pile, session, **kwargs):
		super(Page, self).onPileCreate(pile, session, **kwargs)
		Traveler.onPileCreate(self, pile, session, **kwargs)

class TreasureHunter(Action, Traveler):
	name = 'Treasure Hunter'
	def __init__(self, session, **kwargs):
		super(TreasureHunter, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Warrior 
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(TreasureHunter, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddAction)
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='startTurn' and self.session.events[i][1]['player']!=player:
				previousPlayer = self.session.events[i][1]['player']
				for n in range(i, len(self.session.events)):
					if self.session.events[n][0]=='Gain' and self.session.events[n][1]['player']==previousPlayer: player.resolveEvent(GainFromPile, frm=self.session.piles['Silver'])
					elif player.session.events[n][0]=='turnEnded': return
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.addCard(type(self))

class Warrior(Action, Traveler, Attack):
	name = 'Warrior'
	def __init__(self, session, **kwargs):
		super(Warrior, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.morph = Hero 
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Warrior, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=2)
		self.attackOpponents(player, amnt=len([o for o in player.inPlay if 'TRAVELER' in o.types]))
	def attack(self, player, **kwargs):
		for i in range(kwargs['amnt']):
			card = player.resolveEvent(RequestCard)
			if not card: break
			player.resolveEvent(Discard, frm=player.library, card=card)
			if card.coinPrice.access() in (3, 4) and card.potionPrice.access()==0 and card.debtPrice.access()==0: player.resolveEvent(Trash, frm=player.discardPile, card=card)
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.addCard(type(self))

class Hero(Action, Traveler):
	name = 'Hero'
	def __init__(self, session, **kwargs):
		super(Hero, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Champion 
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(Hero, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		player.gain(restriction=lambda o: 'TREASURE' in o.types)
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.addCard(type(self))
		
class Champion(Action, Duration):
	name = 'Champion'
	class ChampionProtect(DelayedReplacement):
		name = 'ChampionProtect'
		defaultTrigger = 'ResolveAttack'
		def condition(self, **kwargs):
			return kwargs['source']==self.enemy
	def __init__(self, session, **kwargs):
		super(Champion, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.connectCondition(Replacement, trigger='PlayCard', source=self.card, resolve=self.resolveProtect, condition=self.conditionProtect)
		self.connectCondition(Trigger, trigger='PlayCard', source=self.card, resolve=self.resolveAction, condition=self.conditionAction)
		self.coinPrice.set(6)
	def onPlay(self, player, **kwargs):
		player.resolveEvent(AddAction)
	def conditionDestroy(self, **kwargs):
		return kwargs['card']==self.card
	def conditionAction(self, **kwargs):
		return self.owner and self.owner==kwargs['player'] and 'ACTION' in kwargs['card'].types and not kwargs['card']==self.card
	def resolveAction(self, **kwargs):
		self.owner.resolveEvent(AddAction)
	def conditionProtect(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay and 'ATTACK' in kwargs['card'].types and not self.owner==kwargs['player']
	def resolveProtect(self, event, **kwargs):
		self.session.connectCondition(self.ChampionProtect, source=self.card, enemy=event.card)
		return event.spawnClone().resolve()
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(5): pile.addCard(type(self))
	
class Peasant(Action, Traveler):
	name = 'Peasant'
	def __init__(self, session, **kwargs):
		super(Peasant, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Soldier
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(Peasant, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddBuy)
	def onPileCreate(self, pile, session, **kwargs):
		super(Peasant, self).onPileCreate(pile, session, **kwargs)
		Traveler.onPileCreate(self, pile, session, **kwargs)
	
class Soldier(Action, Traveler, Attack):
	name = 'Soldier'
	def __init__(self, session, **kwargs):
		super(Soldier, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.morph = Fugitive 
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Soldier, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		player.resolveEvent(AddCoin, amnt=len([o for o in player.inPlay if 'ATTACK' in o.types and o!=self.card]))
		self.attackOpponents(player)
	def attack(self, player, **kwargs):
		if len(player.hand)>3: player.resolveEvent(Discard, card=player.selectCard(message='Choose discard'))
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.addCard(type(self))
	
class Fugitive(Action, Traveler):
	name = 'Fugitive'
	def __init__(self, session, **kwargs):
		super(Fugitive, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Disciple 
		self.coinPrice.set(4)
	def onPlay(self, player, **kwargs):
		super(Fugitive, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=2)
		player.resolveEvent(AddAction)
		card = player.selectCard(message='Choose discard')
		if card: player.resolveEvent(Discard, card=card)
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.addCard(type(self))

class Disciple(Action, Traveler):
	name = 'Disciple'
	def __init__(self, session, **kwargs):
		super(Disciple, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Teacher 
		self.coinPrice.set(5)
		self.links = []
		self.connectCondition(Replacement, trigger='Destroy', source=self.card, resolve=self.resolveDestroy, condition=self.conditionDestroy)
		self.connectCondition(Replacement, trigger='MoveCard', source=self.card, resolve=self.resolveMoveLink, condition=self.conditionMoveLink)
	def onPlay(self, player, **kwargs):
		super(Disciple, self).onPlay(player, **kwargs)
		self.links = []
		options = [o for o in player.hand if 'ACTION' in o.types]
		if not options: return
		card = options[player.user([o.view() for o in options], 'Choose action')]
		if not player.resolveEvent(CastCard, card=card): return
		self.links.append(card)
		player.resolveEvent(PlayCard, card=card)
		if card.name in self.session.piles: player.resolveEvent(GainFromPile, frm=self.session.piles[card.name])
	def conditionDestroy(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay
	def resolveDestroy(self, event, **kwargs):
		if event.card==self.card and self.links: return
		if event.card in self.links: self.links.remove(event.card)
		if not self.links: event.spawn(Destroy, card=self.card).resolve()
		return event.spawnClone().resolve()
	def conditionMoveLink(self, **kwargs):
		return self.owner and kwargs['player']==self.owner and kwargs['card'] in self.links and kwargs['frm']==self.owner.inPlay
	def resolveMoveLink(self, event, **kwargs):
		self.links.remove(event.card)
		return event.spawnClone().resolve()
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.addCard(type(self))
		
class Teacher(Action, Reserve):
	name = 'Teacher'
	def __init__(self, session, **kwargs):
		super(Teacher, self).__init__(session, **kwargs)
		self.triggerSignal = 'startTurn'
		Reserve.__init__(self, session, **kwargs)
		self.coinPrice.set(6)
	def onPlay(self, player, **kwargs):
		super(Teacher, self).onPlay(player, **kwargs)
		Reserve.onPlay(self, player, **kwargs)
	def call(self, **kwargs):
		tokens = ('Plus Card Token', 'Plus Action Token', 'Plus Buy Token', 'Plus Coin Token')
		choice = self.owner.user(tokens, 'Choose token')
		token = self.owner.tokens[tokens[choice]]
		options = []
		for pile in self.session.piles:
			hasBoon = False
			for pileToken in self.session.piles[pile].tokens:
				if 'BOONTOKEN' in pileToken.types and pileToken.playerOwner==self.owner:
					hasBoon = True
					break
			if not hasBoon and 'ACTION' in self.session.piles[pile].maskot.types: options.append(pile)
		if not options: return
		pile = options[self.owner.user(options, 'Choose pile')]
		if token.owner: self.owner.resolveEvent(MoveToken, frm=token.owner.tokens, to=self.session.piles[pile], token=token)
		else: self.owner.resolveEvent(AddToken, to=self.session.piles[pile], token=token)
	def onPileCreate(self, pile, session, **kwargs):
		Reserve.onPileCreate(self, pile, session, **kwargs)
		for i in range(5): pile.addCard(type(self))
		session.addToken(PlusCard)
		session.addToken(PlusAction)
		session.addToken(PlusBuy)
		session.addToken(PlusCoin)
	
class Ratcatcher(Action, Reserve):
	name = 'Ratcatcher'
	def __init__(self, session, **kwargs):
		super(Ratcatcher, self).__init__(session, **kwargs)
		self.triggerSignal = 'startTurn'
		Reserve.__init__(self, session, **kwargs)
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(Ratcatcher, self).onPlay(player, **kwargs)
		Reserve.onPlay(self, player, **kwargs)
		player.resolveEvent(AddAction)
		player.resolveEvent(Draw)
	def call(self, **kwargs):
		card = self.owner.selectCard('Choose trash')
		if card: self.owner.resolveEvent(Trash, frm=self.owner.hand, card=card)
	def onPileCreate(self, pile, session, **kwargs):
		super(Ratcatcher, self).onPileCreate(pile, session, **kwargs)
		Reserve.onPileCreate(self, pile, session, **kwargs)
		
adventures = [CoinOfTheRealm, Page, Peasant, Ratcatcher]

class Potion(Treasure):
	name = 'Potion'
	def __init__(self, session, **kwargs):
		super(Potion, self).__init__(session, **kwargs)
		self.potionValue.set(1)
		self.coinPrice.set(4)
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(16): pile.addCard(type(self))
		
class Transmute(Action):
	name = 'Transmute'
	def __init__(self, session, **kwargs):
		super(Transmute, self).__init__(session, **kwargs)
		self.potionPrice.set(1)
	def onPlay(self, player, **kwargs):
		super(Transmute, self).onPlay(player, **kwargs)
		card = player.selectCard(message='Choose trash')
		player.resolveEvent(Trash, frm=player.hand, card=card)
		if 'ACTION' in card.types: player.resolveEvent(GainFromPile, frm=self.session.piles['Duchy'])
		if 'TREASURE' in card.types: player.resolveEvent(GainFromPile, frm=self.session.piles['Transmute'])
		if 'VICTORY' in card.types: player.resolveEvent(GainFromPile, frm=self.session.piles['Gold'])
	def onPileCreate(self, pile, session, **kwargs):
		super(Transmute, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
		
alchemy = [Transmute]

class CityQuarter(Action):
	name = 'City Quarter'
	def __init__(self, session, **kwargs):
		super(CityQuarter, self).__init__(session, **kwargs)
		self.debtPrice.set(8)
	def onPlay(self, player, **kwargs):
		super(CityQuarter, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction, amnt=2)
		actions = 0
		for card in player.hand:
			player.resolveEvent(Reveal, card=card)
			if 'ACTION' in card.types: actions += 1
		player.resolveEvent(DrawCards, amnt=actions)

class RoyalBlacksmith(Action):
	name = 'Royal Blacksmith'
	def __init__(self, session, **kwargs):
		super(RoyalBlacksmith, self).__init__(session, **kwargs)
		self.debtPrice.set(8)
	def onPlay(self, player, **kwargs):
		super(RoyalBlacksmith, self).onPlay(player, **kwargs)
		player.resolveEvent(DrawCards, amnt=5)
		for card in copy.copy(player.hand):
			player.resolveEvent(Reveal, card=card)
			if card.name=='Copper': player.resolveEvent(Discard, card=card)
		
class Villa(Action):
	name = 'Villa'
	def __init__(self, session, **kwargs):
		super(Villa, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
		self.connectCondition(Trigger, trigger='Gain', source=self.card, resolve=self.resolveGain, condition=self.conditionGain)
	def onPlay(self, player, **kwargs):
		super(Villa, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction, amnt=2)
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddBuy)
	def conditionGain(self, **kwargs):
		return self.owner and kwargs['card']==self.card
	def resolveGain(self, **kwargs):
		player = self.owner
		player.resolveEvent(AddAction)
		player.resolveEvent(MoveCard, frm=player.discardPile, to=player.hand, card=self.card)
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='actionPhase' or self.session.events[i][0]=='treasurePhase': break
			elif self.session.events[i][0]=='buyPhase' and self.session.events[i][1]['player']==player:
				player.actionPhase()
				player.treasurePhase()
				player.buyPhase()
				break
		
class Gladiator(Action):
	name = 'Gladiator'
	def __init__(self, session, **kwargs):
		super(Gladiator, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Gladiator, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin, amnt=2)
		card = player.selectCard(message='Choose reveal')
		if not card: return
		player.resolveEvent(Reveal, card=card)
		aplayer = self.session.getPreviousPlayer(player)
		for c in aplayer.hand:
			if c.name==card.name:
				if aplayer.user(['no', 'yes'], 'Reveal '+c.view()): 
					aplayer.resolveEvent(Reveal, card=c)
					return
				break
		player.resolveEvent(AddCoin)
		card = self.session.piles['Gladiator/Fortune'].viewTop()
		if card and card.name=='Gladiator': player.resolveEvent(Trash, frm=self.session.piles['Gladiator/Fortune'], card=card)
		
class Fortune(Treasure):
	name = 'Fortune'
	def __init__(self, session, **kwargs):
		super(Fortune, self).__init__(session, **kwargs)
		self.coinPrice.set(8)
		self.debtPrice.set(8)
		self.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
	def onPlay(self, player, **kwargs):
		super(Fortune, self).onPlay(player, **kwargs)
		player.resolveEvent(AddBuy)
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='DoubleMoney' and self.session.events[i][1]['player']==player: return
			elif self.session.events[i][0]=='startTurn': break
		player.resolveEvent(DoubleMoney)
	def conditionGain(self, **kwargs):
		return kwargs['card']==self.card
	def resolveGain(self, **kwargs):
		for card in kwargs['player'].inPlay:
			if card.name=='Gladiator': player.resolveEvent(GainFromPile, self.session.piles['Gold'])

class GladiatorFortune(BaseCard):
	name = 'Gladiator/Fortune'
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(5): pile.addCard(Fortune)
		for i in range(5): pile.addCard(Gladiator)
		
class Capital(Treasure):
	name = 'Capital'
	def __init__(self, session, **kwargs):
		super(Capital, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		self.coinValue.set(6)
		self.connectCondition(Trigger, trigger='Destroy', source=self, resolve=self.resolveDestroy, condition=self.conditionDestroy)
	def onPlay(self, player, **kwargs):
		super(Capital, self).onPlay(player, **kwargs)
		player.resolveEvent(AddBuy)
	def conditionDestroy(self, **kwargs):
		return kwargs['card']==self.card
	def resolveDestroy(self, **kwargs):
		self.owner.resolveEvent(AddDebt, amnt=6)
		self.owner.resolveEvent(PayDebt)

class Settlers(Action):
	name = 'Settlers'
	def __init__(self, session, **kwargs):
		super(Settlers, self).__init__(session, **kwargs)
		self.coinPrice.set(2)
	def onPlay(self, player, **kwargs):
		super(Settlers, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction)
		player.resolveEvent(Draw)
		coppers = [o for o in player.discardPile if o.name=='Copper']
		if coppers and player.user(('no', 'yes'), 'Choose return copper'):
			player.resolveEvent(Reveal, card=coppers[-1])
			player.resolveEvent(MoveCard, frm=player.discardPile, to=player.hand, card=coppers[-1])

class BustlingVillage(Action):
	name = 'Bustling Village'
	def __init__(self, session, **kwargs):
		super(BustlingVillage, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
	def onPlay(self, player, **kwargs):
		super(BustlingVillage, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction, amnt=3)
		player.resolveEvent(Draw)
		coppers = [o for o in player.discardPile if o.name=='Settlers']
		if coppers and player.user(('no', 'yes'), 'Choose return Settlers'):
			player.resolveEvent(Reveal, card=coppers[-1])
			player.resolveEvent(MoveCard, frm=player.discardPile, to=player.hand, card=coppers[-1])

class SettlersBustlingVillage(BaseCard):
	name = 'Settlers/BustlingVillage'
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(5): pile.addCard(BustlingVillage)
		for i in range(5): pile.addCard(Settlers)

class Catapult(Action, Attack):
	name = 'Catapult'
	def __init__(self, session, **kwargs):
		super(Catapult, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Catapult, self).onPlay(player, **kwargs)
		player.resolveEvent(AddCoin)
		card = player.selectCard(message='Choose trash')
		if not card: return
		curse = card.coinPrice.access()>=3
		militia = 'TREASURE' in card.types
		player.resolveEvent(Trash, frm=player.hand, card=card)
		self.attackOpponents(player, curse=curse, militia=militia)
	def attack(self, player, **kwargs):
		if kwargs['militia']:
			while len(player.hand)>3:
				card = player.selectCard(message='Choose discard')
				player.resolveEvent(Discard, card=card)
		if kwargs['curse']: player.resolveEvent(GainFromPile, frm=self.session.piles['Curse'])
		
class Rocks(Treasure):
	name = 'Rocks'
	def __init__(self, session, **kwargs):
		super(Rocks, self).__init__(session, **kwargs)
		self.coinPrice.set(4)
		self.coinValue.set(3)
		self.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.gainSilver, condition=self.condition)
		self.connectCondition(Trigger, trigger='Trash', source=self, resolve=self.gainSilver, condition=self.condition)
	def gainSilver(self, **kwargs):
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='actionPhase' or self.session.events[i][0]=='treasurePhase': break
			elif self.session.events[i][0]=='buyPhase' and self.session.events[i][1]['player']==self.owner:
				self.owner.resolveEvent(GainFromPile, frm=self.session.piles['Silver'], to=self.owner.library)
				return
		self.owner.resolveEvent(GainFromPile, frm=self.session.piles['silver'])
	def condition(self, **kwargs):
		return kwargs['card']==self.card
		
class CatapultRocks(BaseCard):
	name = 'Catapult/Rocks'
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(5): pile.addCard(Rocks)
		for i in range(5): pile.addCard(Catapult)
		
class Crown(Action, Treasure):
	name = 'Crown'
	def __init__(self, session, **kwargs):
		super(Crown, self).__init__(session, **kwargs)
		Treasure.__init__(self, session, **kwargs)
		self.coinPrice.set(5)
		self.links = []
		self.connectCondition(Replacement, trigger='Destroy', source=self.card, resolve=self.resolveDestroy, condition=self.conditionDestroy)
		self.connectCondition(Replacement, trigger='MoveCard', source=self.card, resolve=self.resolveMoveLink, condition=self.conditionMoveLink)
	def onPlay(self, player, **kwargs):
		super(Crown, self).onPlay(player, **kwargs)
		self.links = []
		options = []
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='actionPhase' and self.session.events[i][1]['player']==player:
				options = [o for o in player.hand if 'ACTION' in o.types]
				break
			elif self.session.events[i][0]=='treasurePhase' and self.session.events[i][1]['player']==player:
				options = [o for o in player.hand if 'TREASURE' in o.types]
				break
		if not options: return
		choice = player.user([o.view() for o in options], 'Choose card')
		if not player.resolveEvent(CastCard, card=options[choice]): return
		self.links.append(options[choice])
		player.resolveEvent(PlayCard, card=options[choice])
	def conditionDestroy(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay
	def resolveDestroy(self, event, **kwargs):
		if event.card==self.card and self.links: return
		if event.card in self.links: self.links.remove(event.card)
		if not self.links: event.spawn(Destroy, card=self.card).resolve()
		return event.spawnClone().resolve()
	def conditionMoveLink(self, **kwargs):
		return self.owner and kwargs['player']==self.owner and kwargs['card'] in self.links and kwargs['frm']==self.owner.inPlay
	def resolveMoveLink(self, event, **kwargs):
		self.links.remove(event.card)
		return event.spawnClone().resolve()

class GroundsKeeper(Action):
	name = 'Groundskeeper'
	def __init__(self, session, **kwargs):
		super(GroundsKeeper, self).__init__(session, **kwargs)
		self.coinPrice.set(5)
		self.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
	def onPlay(self, player, **kwargs):
		super(GroundsKeeper, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction)
		player.resolveEvent(Draw)
	def conditionGain(self, **kwargs):
		return self.owner and self.card in self.owner.inPlay and 'VICTORY' in kwargs['card'].types
	def resolveGain(self, **kwargs):
		self.owner.resolveEvent(AddVictory)

class Enchantress(Action, Duration, Attack):
	name = 'Enchantress'
	class EnchantressAttack(DelayedReplacement):
		name = 'EnchantressAttack'
		defaultTrigger = 'ResolveCard'
		defaultTerminatorTrigger = 'turnEnded'
		def condition(self, **kwargs):
			return 'ACTION' in kwargs['card'].types and kwargs['player']==self.attacking
		def resolve(self, event, **kwargs):
			event.spawn(AddAction, amnt=1).resolve()
			event.spawn(Draw).resolve()
		def terminateCondition(self, **kwargs):
			return kwargs['player']==self.attacking
	def __init__(self, session, **kwargs):
		super(Enchantress, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(Enchantress, self).onPlay(player, **kwargs)
		Duration.onPlay(self, player, **kwargs)
		self.attackOpponents(player)
	def duration(self, **kwargs):
		self.owner.resolveEvent(DrawCards, amnt=2)
	def attack(self, player, **kwargs):
		self.session.connectCondition(self.EnchantressAttack, source=self.card, attacking=player)

class ChariotRace(Action):
	name = 'Chariot Race'
	def __init__(self, session, **kwargs):
		super(ChariotRace, self).__init__(session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(BustlingVillage, self).onPlay(player, **kwargs)
		player.resolveEvent(AddAction)
		card = player.resolveEvent(RequestCard)
		if not card: return
		player.resolveEvent(Reveal, card=card)
		player.resolveEvent(MoveCard, frm=player.library, to=player.hand, card=card)
		aplayer = self.session.getNextPlayer(player)
		if card:
			acard = aplayer.resolveEvent(Reveal, card=card)
			if not acard.costLessThan(card): return
		player.resolveEvent(AddCoin)
		player.resolveEvent(AddVictory)
		
class VP(Token):
	name = 'VP Token'
		
class FarmersMarket(Action, Gathering):
	name = "Farmer's Market"
	def __init__(self, session, **kwargs):
		super(ChariotRace, self).__init__(session, **kwargs)
		Gathering.__init__(self, session, **kwargs)
		self.coinPrice.set(3)
	def onPlay(self, player, **kwargs):
		super(BustlingVillage, self).onPlay(player, **kwargs)
		player.resolveEvent()
		
		
empires = [CityQuarter, RoyalBlacksmith, Villa, GladiatorFortune, Capital, SettlersBustlingVillage, CatapultRocks, Crown, GroundsKeeper, Enchantress, ChariotRace]