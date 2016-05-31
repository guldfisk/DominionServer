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
		kwargs['circumstance']['player'].resolveEvent(AddVictory, amnt=2)
		
class Fountain(Landmark):
	name = 'Fountain'
	def onGameEnd(self, player, **kwargs):
		if len([o for o in player.owns if o.name=='Copper'])>=10: player.resolveEvent(AddVictory, amnt=15)
	
class Keep(Landmark):
	name = 'Keep'
	def onGameEnd(self, player, **kwargs):
		treasures = set([o.name for o in player.owns if 'TREASURE' in o.types])
		for aplayer in self.session.getOtherPlayers(player):
			for treasure in copy.copy(treasures): 
				if len([o for o in aplayer.owns if o.name==treasure])>len([o for o in player.owns if o.name==treasure]): treasures.remove(treasure)
		player.resolveEvent(AddVictory, amnt=5*len(treasures))
	
empiresLandmarks = [Battlefield, Fountain, Keep]