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

empiresLandmarks = [Battlefield, Fountain, Keep, Tomb, WolfDen]

landmarkSets = {
	'empiresLandmarks': empiresLandmarks
}