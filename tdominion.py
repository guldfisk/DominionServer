from cards import *

def logFunc(signal, **kwargs):
	if signal=='startTurn':
		print('-'*36)
	elif signal=='beginRound':
		print('*'*36)
	print('>'+signal, end='::'+' '*(18-len(signal)))
	for key in kwargs:
		if key=='sender': continue
		print(key, end=': ')
		if hasattr(kwargs[key], 'playerName'): print(kwargs[key].playerName, end=', ')
		elif hasattr(kwargs[key], 'name'): print(kwargs[key].name, end=', ')
		else: print(str(kwargs[key]), end=', ')
	print('')
	if signal=='startTurn':
		pass#kwargs['player'].view()
	elif signal=='actionPhase':
		print('Actions: '+str(kwargs['player'].actions))
	elif signal=='buyPhase':
		print(kwargs['player'].game.getPilesView())
		print('Coins: '+str(kwargs['player'].coins)+'\tBuys: '+str(kwargs['player'].buys))
	elif signal=='playAction':
		pass

def makeBasePiles():
	for card in baseSetBase + baseSet:
		piles[card.name] = Pile(card)
	print(list(piles))
		
def main():
	makeBasePiles()
	for i in range(4):
		p1.take(piles['Silver'])
		p2.take(piles['Silver'])
		p1.take(piles['Gold'])
		p2.take(piles['Gold'])
	game()
	

if __name__=='__main__':
	dp.connect(logFunc)
	p1 = Player()
	p2 = Player(name='p2')
	activePlayer = p1
	main()
