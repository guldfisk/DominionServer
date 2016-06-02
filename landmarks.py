from cards import *

class Battlefield(Landmark):
	name = 'Battlefield'
	def __init__(self, session, **kwargs):
		super(Battlefield, self).__init__(session, **kwargs)
		self.points = len(session.players)*6
		session.connectCondition(Trigger, trigger='Gain', source=self, resolve=self.resolveGain, condition=self.conditionGain)
	def view(self, **kwargs):
		return self.name+'('+str(self.points)+')'
	def conditionGain(self, **kwargs):
		return 'VICTORY' in kwargs['card'].types
	def resolveGain(self, **kwargs):
		if not self.points: return
		self.points -= 2
		kwargs['player'].resolveEvent(AddVictory, amnt=2)
		
class Fountain(Landmark):
	name = 'Fountain'
	def onGameEnd(self, player, **kwargs):
		if [o.name for o in player.owns].count('Copper')>=10: player.resolveEvent(AddVictory, amnt=15)
	
class Keep(Landmark):
	name = 'Keep'
	def onGameEnd(self, player, **kwargs):
		treasures = set([o.name for o in player.owns if 'TREASURE' in o.types])
		for aplayer in self.session.getOtherPlayers(player):
			for treasure in copy.copy(treasures):
				if [o.name for o in aplayer.owns].count(treasure)>[o.name for o in player.owns].count(treasure): treasures.remove(treasure)
		player.resolveEvent(AddVictory, amnt=5*len(treasures))

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
		for card in uniques:
			if cards.count(card)==1: player.resolveEvent(AddVictory, amnt=-3)

empiresLandmarks = [Battlefield, Fountain, Keep, Tomb, WolfDen]