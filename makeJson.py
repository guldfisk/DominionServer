from cards import *
from devents import *
from landmarks import *
import json

def make():
		d = {}
		for exp in cardSets:
			game = Game()
			game.makePiles(cardSets[exp])
			#game.makeDEvents(allDEvents)
			#game.makeLandmarks(landmarks)
			d[exp] = set()
			for pile in game.piles:
				d[exp].add(pile)
				for name in [o.name for o in game.piles[pile]]: d[exp].add(name)
			for pile in game.NSPiles:
				d[exp].add(pile)
				for name in [o.name for o in game.NSPiles[pile]]: d[exp].add(name)
			d[exp] = list(d[exp])
		print(d)
		file = open('cards.json', 'w')
		file.write(json.dumps(d))
		file.close()
		
		d = {}
		game = Game()
		game.makeDEvents(adventuresDEvents)
		d['adventures'] = set()
		for event in game.eventSupply:
			d['adventures'].add(event)
		d['adventures'] = list(d['adventures'])
		print(d)
		file = open('events.json', 'w')
		file.write(json.dumps(d))
		file.close()
		

if __name__=='__main__':
	"""
	cardSetsD = {key: {o.name: o for o in cardSets[key]} for key in cardSets}
	deventSetsD = {key: {o.name: o for o in deventSets[key]} for key in deventSets}
	landSetsD = {key: {o.name: o for o in landmarkSets[key]} for key in landmarkSets}
	allCards = dictMerge(*[cardm[key] for key in cardm])
	allDEvents = dictMerge(*[deventm[key] for key in deventm])
	allLands = dictMerge(*[landm[key] for key in landm])
	"""
	make()