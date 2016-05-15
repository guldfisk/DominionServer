from dombase import *

class Copper(Treasure):
	name = 'Copper'
	def __init__(self, game, **kwargs):
		super(Copper, self).__init__(game, **kwargs)
		self.coinValue.set(1)
		self.coinPrice.set(0)
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(60-len(game.players)*7):
			pile.append(type(self)(game))
			
			
baseSetBase = [Copper]