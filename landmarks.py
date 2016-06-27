from cards import *

class Battlefield(Landmark):
	name = 'Battlefield'
	def __init__(self, session, **kwargs):
		super(Battlefield, self).__init__(session, **kwargs)
		for i in range(6*len(session.players)): session.resolveEvent(AddToken, token=VP(session), to=self)
		session.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
	def conditionGain(self, **kwargs):
		return 'VICTORY' in kwargs['card'].types
	def resolveGain(self, **kwargs):
		kwargs['player'].resolveEvent(TakeVPs, amnt=2, frm=self)
		
class Fountain(Landmark):
	name = 'Fountain'
	def onGameEnd(self, player, **kwargs):
		if [o.name for o in player.owns].count('Copper')>=10: return 15
	
class Keep(Landmark):
	name = 'Keep'
	def onGameEnd(self, player, **kwargs):
		treasures = set([o.name for o in player.owns if 'TREASURE' in o.types])
		for aplayer in self.session.getOtherPlayers(player):
			for treasure in copy.copy(treasures):
				if [o.name for o in aplayer.owns].count(treasure)>[o.name for o in player.owns].count(treasure): treasures.remove(treasure)
		return 5*len(treasures)

class Tomb(Landmark):
	name = 'Tomb'
	def __init__(self, session, **kwargs):
		super(Tomb, self).__init__(session, **kwargs)
		session.connectCondition(Trigger, trigger='Trash', source=self, resolve=self.resolveTrash)
	def resolveTrash(self, **kwargs):
		kwargs['player'].resolveEvent(AddVictory)

class WolfDen(Landmark):
	name = 'Wolf Den'
	def onGameEnd(self, player, **kwargs):
		cards = [o.name for o in player.owns]
		uniques = set(cards)
		return len([o for o in uniques if cards.count(o)==1])*-3

class Aquaduct(Landmark):
	name = 'Aquaduct'
	class AquaductSetup(DelayedTrigger):
		name = 'AquaductSetup'
		defaultTrigger = 'globalSetup'
		def resolve(self, **kwargs):
			for pile in ('Silver', 'Gold'):
				for i in range(8): self.source.session.resolveEvent(AddToken, to=self.source.session.piles[pile], token=VP(self.source.session))
	def __init__(self, session, **kwargs):
		super(Aquaduct, self).__init__(session, **kwargs)
		session.connectCondition(self.AquaductSetup, source=self)
		session.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
		session.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveTreasure, condition=self.conditionTreasure)
	def conditionGain(self, **kwargs):
		return 'VICTORY' in kwargs['card'].types
	def resolveGain(self, **kwargs):
		kwargs['player'].resolveEvent(TakeVPs, frm=self)
	def conditionTreasure(self, **kwargs):
		return kwargs['card'].name in ('Silver', 'Gold')
	def resolveTreasure(self, **kwargs):
		for token in kwargs['frm'].tokens:
			if token.name=='VP Token':
				self.session.resolveEvent(MoveToken, frm=kwargs['frm'], to=self, token=token)
				break
		
class Arena(Landmark):
	name = 'Arena'
	def __init__(self, session, **kwargs):
		super(Arena, self).__init__(session, **kwargs)
		for i in range(6*len(session.players)): session.resolveEvent(AddToken, token=VP(session), to=self)
		session.connectCondition(Trigger, trigger='buyPhase', source=self, resolve=self.resolveBuyPhase)
	def resolveBuyPhase(self, **kwargs):
		card = kwargs['player'].selectCard(optional=True, message='Choose Arena discard', restriction=lambda o: 'ACTION' in o.types)
		if not card: return
		kwargs['player'].resolveEvent(Discard, card=card)
		kwargs['player'].resolveEvent(TakeVPs, amnt=2, frm=self)
		
class BanditFort(Landmark):
	name = 'Bandit Fort'
	def onGameEnd(self, player, **kwargs):
		cards = [o.name for o in player.owns]
		return len([o for o in cards if o=='Silver' or o=='Gold'])*-2
		
class Basilica(Landmark):
	name = 'Basilica'
	def __init__(self, session, **kwargs):
		super(Basilica, self).__init__(session, **kwargs)
		for i in range(6*len(session.players)): session.resolveEvent(AddToken, token=VP(session), to=self)
		session.connectCondition(Trigger, trigger='Buy', source=self, resolve=self.resolveBuy, condition=self.conditionBuy)
	def conditionBuy(self, **kwargs):
		return kwargs['player'].coins>=2
	def resolveBuy(self, **kwargs):
		kwargs['player'].resolveEvent(TakeVPs, amnt=2, frm=self)
		
class Baths(Landmark):
	name = 'Baths'
	def __init__(self, session, **kwargs):
		super(Baths, self).__init__(session, **kwargs)
		for i in range(6*len(session.players)): session.resolveEvent(AddToken, token=VP(session), to=self)
		session.connectCondition(Trigger, trigger='endTurn', source=self, resolve=self.resolveTurn, condition=self.conditionTurn)
	def conditionTurn(self, **kwargs):
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='Gain' and self.session.events[i][1]['player']==player: return False
			elif self.session.events[i][0]=='startTurn': break
		return True
	def resolveTurn(self, **kwargs):
		kwargs['player'].resolveEvent(TakeVPs, amnt=2, frm=self)

class Colonnade(Landmark):
	name = 'Colonnade'
	def __init__(self, session, **kwargs):
		super(Colonnade, self).__init__(session, **kwargs)
		for i in range(6*len(session.players)): session.resolveEvent(AddToken, token=VP(session), to=self)
		session.connectCondition(Trigger, trigger='Buy', source=self, resolve=self.resolveBuy, condition=self.conditionBuy)
	def conditionBuy(self, **kwargs):
		return 'ACTION' in kwargs['card'].types and kwargs['card'].name in [o.name for o in kwargs['player'].inPlay]
	def resolveBuy(self, **kwargs):
		kwargs['player'].resolveEvent(TakeVPs, amnt=2, frm=self)
		
class DefiledShrine(Landmark):
	name = 'Defiled Shrine'
	class DefiledShrineSetup(DelayedTrigger):
		name = 'DefiledShrineSetup'
		defaultTrigger = 'globalSetup'
		def resolve(self, **kwargs):
			for pile in self.source.piles:
				if 'ACTION' in self.source.session.piles[pile].maskot.types and not 'GATHERING' in self.source.session.piles[pile].maskot.types :
					for i in range(2): self.source.session.resolveEvent(AddToken, to=self.source.session.piles[pile], token=VP(self.source.session))
	def __init__(self, session, **kwargs):
		super(DefiledShrine, self).__init__(session, **kwargs)
		session.connectCondition(self.DefiledShrineSetup, source=self)
		session.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
		session.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveAction, condition=self.conditionAction)
	def conditionGain(self, **kwargs):
		return kwargs['card'].name=='Curse'
	def resolveGain(self, **kwargs):
		kwargs['player'].resolveEvent(TakeVPs, frm=self)
	def conditionAction(self, **kwargs):
		return 'ACTION' in kwargs['card']
	def resolveAction(self, **kwargs):
		for token in kwargs['frm'].tokens:
			if token.name=='VP Token':
				self.session.resolveEvent(MoveToken, frm=kwargs['frm'], to=self, token=token)
				break

class Labyrinth(Landmark):
	name = 'Labyrinth'
	def __init__(self, session, **kwargs):
		super(Labyrinth, self).__init__(session, **kwargs)
		for i in range(6*len(session.players)): session.resolveEvent(AddToken, token=VP(session), to=self)
		session.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
	def conditionGain(self, **kwargs):
		gained = 0
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='Gain' and self.session.events[i][1]['player']==kwargs['player']: gained+=1
			elif self.session.events[i][0]=='startTurn': break
		return gained==2
	def resolveGain(self, **kwargs):
		kwargs['player'].resolveEvent(TakeVPs, amnt=2, frm=self)
		
"""		
class MountainPass(Landmark):
	name = 'Mountain Pass'
	class FirstProvince(DelayedTrigger):
		name = 'FirstProvince'
		defaultTrigger = 'Gain'
		def condition(self, **kwargs):
			return kwargs['card'}.name=='Province'
		def resolve(self, **kwargs):
			self.session.connectCondition(self.Bidding, source=self.source, player=kwargs['player'])
	class Bidding(DelayedTrigger):
		name = 'Bidding'
		defaultTrigger = 'turnEnded'
		def resolve(self, **kwargs):
			high = 0
			winner = 0
			for player in self.session.getPlayers(self.session.getNextPlayer(self.player)):
				bid = player.user(list(range(high, 41)), 'Choose bid')
				player.resolveEvent(Message, content=bid)
				if bid>high: winner = 10
	def __init__(self, session, **kwargs):
		super(MountainPass, self).__init__(session, **kwargs)
		session.connectCondition(self.FirstProvince, source=self)
"""
				
empiresLandmarks = [Battlefield, Fountain, Keep, Tomb, WolfDen, Aquaduct, Arena, BanditFort, Basilica, Baths, Colonnade, DefiledShrine, Labyrinth]

landmarkSets = {
	'empiresLandmarks': empiresLandmarks
}