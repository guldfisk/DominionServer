from dombase import *

class Copper(Treasure, CardAdd):
	name = 'Copper'
	def __init__(self, game, **kwargs):
		super(Copper, self).__init__(game, **kwargs)
		self.value = 1
		self.price = 0
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(60-len(game.players)*7):
			pile.append(type(self)(game))

class Silver(Treasure, CardAdd):
	name = 'Silver'
	def __init__(self, game, **kwargs):
		super(Silver, self).__init__(game, **kwargs)
		self.value = 2
		self.price = 3
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(40):
			pile.append(type(self)(game))
		
class Gold(Treasure, CardAdd):
	name = 'Gold'
	def __init__(self, game, **kwargs):
		super(Gold, self).__init__(game, **kwargs)
		self.value = 3
		self.price = 6
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(30):
			pile.append(type(self)(game))
		
class Estate(Victory, CardAdd):
	name = 'Estate'
	def __init__(self, game, **kwargs):
		super(Estate, self).__init__(game, **kwargs)
		self.value = 1
		self.price = 2
	def onPileCreate(self, pile, game, **kwargs):
		if len(game.players)>2:
			amnt = 12
		else:
			amnt = 8
		for i in range(amnt+len(game.players)*3):
			pile.append(type(self)(game))

class Duchy(Victory, CardAdd):
	name = 'Duchy'
	def __init__(self, game, **kwargs):
		super(Duchy, self).__init__(game, **kwargs)
		self.value = 3
		self.price = 5

class Province(Victory, CardAdd):
	name = 'Province'
	def __init__(self, game, **kwargs):
		super(Province, self).__init__(game, **kwargs)
		self.value = 6
		self.price = 8
	def onPileCreate(self, pile, game, **kwargs):
		super(Province, self).onPileCreate(pile, game)
		pile.terminator = True
		
class Curse(Cursed, CardAdd):
	name = 'Curse'
	def __init__(self, game, **kwargs):
		super(Curse, self).__init__(game, **kwargs)
		self.value = -1
		self.price = 0
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(10*np.max((len(game.players)-1, 1))):
			pile.append(type(self)(game))
		
baseSetBase = [Copper, Silver, Gold, Estate, Duchy, Province, Curse]

class Cellar(Action, CardAdd):
	name = 'Cellar'
	def __init__(self, game, **kwargs):
		super(Cellar, self).__init__(game, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Cellar, self).onPlay(player, **kwargs)
		player.addAction()
		discardedAmnt = 0
		while player.hand:
			choice = player.user([o.name for o in player.hand]+['EndCellar'], 'Choose discard')
			if choice+1>len(player.hand): break
			player.discard(choice)
			discardedAmnt += 1
		player.draw(amnt=discardedAmnt)
		
class Chapel(Action, CardAdd):
	name = 'Chapel'
	def __init__(self, game, **kwargs):
		super(Chapel, self).__init__(game, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Chapel, self).onPlay(player, **kwargs)
		if not player.hand: return
		options = copy.copy(player.hand)
		trashed = []
		for i in range(4):
			choice = player.user([o.name for o in options]+['EndChapel'], 'Choose trash')
			if choice+1>len(options): break
			trashed.append(options.pop(choice))
			if not options: break
		for card in trashed:
			for i in range(len(player.hand)):
				if player.hand[i]==card:
					player.trash(i)
					break
			
class Moat(Action, Reaction, CardAdd):
	name = 'Moat'
	def __init__(self, game, **kwargs):
		super(Moat, self).__init__(game, **kwargs)
		Reaction.__init__(self, game, **kwargs)
		self.price = 2
		self.signal = 'attack'
	def onPlay(self, player, **kwargs):
		super(Moat, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and self in self.owner.hand and self.owner.user(('no', 'yes'), 'Use moat'):
			self.owner.reveal(self)
			return True
	def connect(self, **kwargs):
		kwargs['player'].game.dp.connect(self.trigger, signal=self.signal)
	def disconnect(self, **kwargs):
		kwargs['player'].game.dp.connect(self.trigger, signal=self.signal)
	def onGain(self, player, **kwargs):
		self.connect(player=player)
	def onTrash(self, player, **kwargs):
		self.disconnect(player=player)
	def onReturn(self, player, **kwargs):
		self.disconnect(player=player)
		
class Chancellor(Action, CardAdd):
	name = 'Chancellor'
	def __init__(self, game, **kwargs):
		super(Chancellor, self).__init__(game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Chancellor, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		if player.user(('no', 'yes'), 'Discard library'):
			player.game.dp.send(signal='Announce', message='Discard deck')
			while player.library:
				player.discardPile.append(player.library.pop())
		
class Village(Action, CardAdd):
	name = 'Village'
	def __init__(self, game, **kwargs):
		super(Village, self).__init__(game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Village, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction(amnt=2)
		
class Woodcutter(Action, CardAdd):
	name = 'Woodcutter'
	def __init__(self, game, **kwargs):
		super(Woodcutter, self).__init__(game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Woodcutter, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		player.addBuy()
		
class Workshop(Action, CardAdd):
	name = 'Workshop'
	def __init__(self, game, **kwargs):
		super(Workshop, self).__init__(game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Workshop, self).onPlay(player, **kwargs)
		options = []
		for pile in player.game.piles:
			if player.game.piles[pile].viewTop() and player.game.piles[pile].viewTop().getPrice(player)<5 and player.game.piles[pile].viewTop().getPotionPrice(player)<1:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.game.piles[options[choice]])
		
class Bureaucrat(Action, Attack, CardAdd):
	name = 'Bureaucrat'
	def __init__(self, game, **kwargs):
		super(Bureaucrat, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Bureaucrat, self).onPlay(player, **kwargs)
		player.gain(player.game.piles['Silver'].gain(), to=player.library, fromz=player.game.piles['Silver'].gain())
		for aplayer in player.game.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		hasVictory = False
		for card in player.hand:
			if 'VICTORY' in card.types:
				hasVictory = True
				break
		if not hasVictory:
			for card in player.hand:
				player.reveal(card)
			return
		while True:
			choice = player.user([o.name for o in player.hand], 'Choose top')
			if not 'VICTORY' in player.hand[choice].types: continue
			player.reveal(player.hand[choice])
			player.library.append(player.hand.pop(choice))
			break

class Feast(Action, CardAdd):
	name = 'Feast'
	def __init__(self, game, **kwargs):
		super(Feast, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Feast, self).onPlay(player, **kwargs)
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.trashCard(player.getFromPlay(i))
				break
		options = []
		for pile in player.game.piles:
			if player.game.piles[pile].viewTop() and player.game.piles[pile].viewTop().getPrice(player)<6 and player.game.piles[pile].viewTop().getPotionPrice(player)<1:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.game.piles[options[choice]])
		
class Gardens(Victory, CardAdd):
	name = 'Gardens'
	def __init__(self, game, **kwargs):
		super(Gardens, self).__init__(game, **kwargs)
		self.price = 4
	def onGameEnd(self, player, **kwargs):
		player.addVictory(amnt=m.floor(len(player.library)/10))
	
class Militia(Action, Attack, CardAdd):
	name = 'Militia'
	def __init__(self, game, **kwargs):
		super(Militia, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Militia, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for aplayer in player.game.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		while len(player.hand)>3:
			choice = player.user([o.name for o in player.hand], 'Choose discard')
			player.discard(choice)

class Moneylender(Action, CardAdd):
	name = 'Moneylender'
	def __init__(self, game, **kwargs):
		super(Moneylender, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Moneylender, self).onPlay(player, **kwargs)
		while True:
			choice = player.user([o.name for o in player.hand]+['EndMoneylender'], 'Choose trash')
			if choice+1>len(player.hand): break
			if player.hand[choice].name=='Copper':
				player.trash(choice)
				player.addCoin(amnt=3)
				break
				
class Remodel(Action, CardAdd):
	name = 'Remodel'
	def __init__(self, game, **kwargs):
		super(Remodel, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Remodel, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		coinVal, potionVal = player.hand[choice].getPrice(player), player.hand[choice].getPotionPrice(player)
		player.trash(choice)
		options = []
		for pile in player.game.piles:
			if player.game.piles[pile].viewTop() and player.game.piles[pile].viewTop().getPrice(player)<=coinVal+2 and player.game.piles[pile].viewTop().getPotionPrice(player)<=potionVal: options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.game.piles[options[choice]])
		
class Smithy(Action, CardAdd):
	name = 'Smithy'
	def __init__(self, game, **kwargs):
		super(Smithy, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Smithy, self).onPlay(player, **kwargs)
		player.draw(amnt=3)
		
class Spy(Action, Attack, CardAdd):
	name = 'Spy'
	def __init__(self, game, **kwargs):
		super(Spy, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Spy, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
		for aplayer in player.game.getPlayers(player):
			aplayer.attack(self.attack, self, controller=player)
	def attack(self, player, **kwargs):
		if not player.revealPosition(-1, fromZ=player.library): return
		if kwargs['controller'].user(('Top', 'Bottom'), ''):
			player.game.dp.send(signal='spyBottom')
			player.library.insert(0, player.library.pop())
		else:
			player.game.dp.send(signal='spyTop')

class Thief(Action, Attack, CardAdd):
	name = 'Thief'
	def __init__(self, game, **kwargs):
		super(Thief, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Thief, self).onPlay(player, **kwargs)
		for aplayer in player.game.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self, controller=player)
	def attack(self, player, **kwargs):
		cards = player.getCards(2)
		options = []
		for card in cards:
			player.reveal(card)
			if card and 'TREASURE' in card.types:
				options.append(card)
		if not options: return
		choice = kwargs['controller'].user([o.name for o in options], 'Choose trash')
		gain = kwargs['controller'].user(('No', 'Yes'), 'Gain')
		for card in copy.copy(cards):
			if card==options[choice]:
				player.trashCard(card)
				if gain: kwargs['controller'].gain(trash.pop())
			else: player.discardCard(card)
			
class ThroneRoom(Action, CardAdd):
	name = 'Throne Room'
	def __init__(self, game, **kwargs):
		super(ThroneRoom, self).__init__(game, **kwargs)
		self.price = 4
		self.links = []
	def onPlay(self, player, **kwargs):
		super(ThroneRoom, self).onPlay(player, **kwargs)
		self.links = []
		options = []
		for card in player.hand:
			if 'ACTION' in card.types:
				options.append(card)
		if not options: return
		choice = player.user([o.name for o in options], 'Choose action')
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]:
				player.inPlay.append(player.hand.pop(i))
				break
		self.links.append(options[choice])
		player.game.dp.connect(self.trigger, signal='destroy')
		for i in range(2): player.playAction(options[choice])
	def onDestroy(self, player, **kwargs):
		if self.links: return True
	def onLeavePlay(self, player, **kwargs):
		if self.links: player.game.dp.disconnect(self.trigger, signal='destroy')
	def trigger(self, signal, **kwargs):
		for i in range(len(self.links)-1, -1, -1):
			if self.links[i]==kwargs['card']: self.links.pop(i)
		if self.links: return
		for i in range(len(self.owner.inPlay)):
			if self.owner.inPlay[i]==self:
				self.owner.destroyCard(self.owner.inPlay.pop(i))
				break
		
class CouncilRoom(Action, CardAdd):
	name = 'Council Room'
	def __init__(self, game, **kwargs):
		super(CouncilRoom, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(CouncilRoom, self).onPlay(player, **kwargs)
		player.draw(amnt=3)
		player.addBuy()
		for aplayer in player.game.getPlayers(player):
			aplayer.draw()
			
class Festival(Action, CardAdd):
	name = 'Festival'
	def __init__(self, game, **kwargs):
		super(Festival, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Festival, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		player.addAction(amnt=2)
		player.addBuy()
		
class Laboratory(Action, CardAdd):
	name = 'Laboratory'
	def __init__(self, game, **kwargs):
		super(Laboratory, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Laboratory, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		player.addAction()
		
class Library(Action, CardAdd):
	name = 'Library'
	def __init__(self, game, **kwargs):
		super(Library, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Library, self).onPlay(player, **kwargs)
		aside = []
		while len(player.hand)<8 and not player.draw()=='Empty':
			if 'ACTION' in player.hand[-1].types and not player.user((player.hand[-1].name, 'NotSetAside'), ''):
				actionCard = player.hand.pop()
				player.reveal(actionCard)
				aside.append(actionCard)
		while aside: player.discard(aside.pop())
			
class Market(Action, CardAdd):
	name = 'Market'
	def __init__(self, game, **kwargs):
		super(Market, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Market, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		player.addCoin()
		player.addBuy()
		
class Mine(Action, CardAdd):
	name = 'Mine'
	def __init__(self, game, **kwargs):
		super(Mine, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Mine, self).onPlay(player, **kwargs)
		options = []
		for card in player.hand:
			if 'TREASURE' in card.types:
				options.append(card)
		if not options: return
		choice = player.user([o.name for o in options], 'Choose treasure trash')
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]:
				coinVal, potionVal = player.hand[i].getPrice(player), player.hand[i].getPotionPrice(player)
				player.trash(i)
				break
		options = []
		for pile in player.game.piles:
			if 'TREASURE' in player.game.piles[pile].viewTop().types and player.game.piles[pile].viewTop().getPrice(player)<=coinVal+3 and player.game.piles[pile].viewTop().getPotionPrice(player)<=potionVal:
				options.append(player.game.piles[pile])
		if not options: return
		choice = player.user([o.name for o in options], 'Choose gain')
		player.gainFromPile(options[choice])
	
class Witch(Action, Attack, CardAdd):
	name = 'Witch'
	def __init__(self, game, **kwargs):
		super(Witch, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Witch, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		for aplayer in player.game.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self, controller=player)
	def attack(self, player, **kwargs):
		player.gainFromPile(player.game.piles['Curse'])
		
class Adventurer(Action, CardAdd):
	name = 'Adventurer'
	def __init__(self, game, **kwargs):
		super(Adventurer, self).__init__(game, **kwargs)
		self.price = 6
	def onPlay(self, player, **kwargs):
		super(Adventurer, self).onPlay(player, **kwargs)
		aside = []
		foundTreasure = []
		while len(foundTreasure)<2 and player.revealPosition(-1, fromZ=player.library):
			card = player.library.pop()
			if 'TREASURE' in card.types: foundTreasure.append(card)
			else: aside.append(card)
		for treasure in foundTreasure: player.hand.append(treasure)
		for card in aside: player.discardCard(card)
	
baseSet = [Cellar, Chapel, Moat, Chancellor, Village, Woodcutter, Workshop, Bureaucrat, Feast, Gardens, Militia, Remodel, Smithy, Spy, Thief, ThroneRoom, CouncilRoom, Festival, Laboratory, Library, Market, Mine, Witch, Adventurer]

class Loan(Treasure, CardAdd):
	name = 'Loan'
	def __init__(self, game, **kwargs):
		super(Loan, self).__init__(game, **kwargs)
		self.value = 1
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Loan, self).onPlay(player, **kwargs)
		aside = []
		card = None
		treasure = None
		while True:
			card = player.getCard()
			if card=='Empty': break
			player.reveal(card)
			if 'TREASURE' in card.types:
				treasure = card
				break
			aside.append(card)
		if treasure:
			if player.user(('Trash', 'Discard'), ''): player.discard(treasure)
			else: player.trashCard(treasure)
		while aside:
			player.discardCard(aside.pop())

class TradeToken(Token, CardAdd):
	name = 'TradeToken'
	def __init__(self, game, **kwargs):
		super(TradeToken, self).__init__(game, **kwargs)
		game.dp.connect(self.onGain, signal='gain')
	def onGain(self, signal, **kwargs):
		if 'fromz' in kwargs and kwargs['fromz']==self.owner:
			for i in range(len(self.owner.tokens)):
				if self.owner.tokens[i]==self:
					self.game.globalMats['TradeRouteMat'].append(self.owner.tokens.pop(i))
					self.owner.removeToken(self, self.game)
					break
						
class TradeRoute(Action, CardAdd):
	name = 'Trade Route'
	def __init__(self, game, **kwargs):
		super(TradeRoute, self).__init__(game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(TradeRoute, self).onPlay(player, **kwargs)
		player.addCoin(amnt=len(player.game.globalMats['TradeRouteMat']))
		if player.hand: player.trash(player.user([o.name for o in player.hand], 'Choose trash'))
	def addTokens(self, **kwargs):
		for pile in kwargs['game'].piles:
			if kwargs['game'].piles[pile].viewTop() and 'VICTORY' in kwargs['game'].piles[pile].viewTop().types: kwargs['game'].piles[pile].addToken(TradeToken(kwargs['game']), kwargs['game'])
	def onPileCreate(self, pile, game, **kwargs):
		super(TradeRoute, self).onPileCreate(pile, game, **kwargs)
		game.delayedActions.append([self.addTokens, {'game': game}])
		game.addGlobalMat('TradeRouteMat')
			
class Watchtower(Action, Reaction, CardAdd):
	name = 'Watchtower'
	def __init__(self, game, **kwargs):
		super(Watchtower, self).__init__(game, **kwargs)
		Reaction.__init__(self, game, **kwargs)
		self.price = 3
		self.signal = 'gain'
	def onPlay(self, player, **kwargs):
		super(Watchtower, self).onPlay(player, **kwargs)
		while len(player.hand)<6 and not player.draw()=='Empty': pass
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and self in self.owner.hand and self.owner.user(('no', 'UseWatchTower'), ''):
			self.owner.reveal(self)
			if self.owner.user(('top', 'trash'), ''): kwargs['kwargs']['to'] = trash
			else: kwargs['kwargs']['to'] = self.owner.library
	def onGain(self, player, **kwargs):
		self.connect()
	def onTrash(self, player, **kwargs):
		self.disconnect()
	def onReturn(self, player, **kwargs):
		self.disconnect()
		
class Bishop(Action, CardAdd):
	name = 'Bishop'
	def __init__(self, game, **kwargs):
		super(Bishop, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Bishop, self).onPlay(player, **kwargs)		
		player.addCoin()
		player.addVictory()
		if player.hand:
			choice = player.user([o.name for o in player.hand], 'Choose trash')
			player.addVictory(amnt=m.floor(player.hand[choice].getPrice(player)/2))
			player.trash(choice)
		for aplayer in player.game.getPlayers(player):
			if aplayer==player: continue
			choice = aplayer.user([o.name for o in aplayer.hand]+['NoTrash'], 'Choose trash')
			if choice+1>len(aplayer.hand): continue
			aplayer.trash(choice)
			
class Monument(Action, CardAdd):
	name = 'Monument'
	def __init__(self, game, **kwargs):
		super(Monument, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Monument, self).onPlay(player, **kwargs)
		player.addVictory()
		player.addCoin(amnt=2)
		
class Quarry(Treasure, CardAdd):
	name = 'Quarry'
	def __init__(self, game, **kwargs):
		super(Quarry, self).__init__(game, **kwargs)
		self.price = 4
		self.value = 1
	def onPlay(self, player, **kwargs):
		super(Quarry, self).onPlay(player, **kwargs)
		for card in player.game.allCards:
			if 'ACTION' in card.types: card.price-=2
	def onLeavePlay(self, player, **kwargs):
		for card in player.game.allCards:
			if 'ACTION' in card.types: card.price+=2
			
class Talisman(Treasure, CardAdd):
	name = 'Talisman'
	def __init__(self, game, **kwargs):
		super(Talisman, self).__init__(game, **kwargs)
		self.price = 4
		self.value = 1
	def onPlay(self, player, **kwargs):
		super(Talisman, self).onPlay(player, **kwargs)
		self.connect()
	def onLeavePlay(self, player, **kwargs):
		self.disconnect()
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and 'pile' in kwargs and kwargs['pile'].viewTop() and not 'VICTORY' in kwargs['pile'].viewTop().types: self.owner.gainFromPile(kwargs['pile'])
	def connect(self, **kwargs):
		self.owner.game.dp.connect(self.trigger, signal='buy')
	def disconnect(self, **kwargs):
		self.owner.game.dp.connect(self.trigger, signal='buy')
	
class WorkersVillage(Action, CardAdd):
	name = "Worker's Village"
	def __init__(self, game, **kwargs):
		super(WorkersVillage, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(WorkersVillage, self).onPlay(player, **kwargs)	
		player.addAction(amnt=2)
		player.draw()
		player.addBuy()
		
class City(Action, CardAdd):
	name = 'City'
	def __init__(self, game, **kwargs):
		super(City, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(City, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		if len(player.game.emptyPiles)>0:
			player.draw(amnt=2)
			if len(player.game.emptyPiles)>1:
				player.addCoin()
				player.addBuy()
		else: player.draw()
		
class Contraband(Treasure, CardAdd):
	name = 'Contraband'
	def __init__(self, game, **kwargs):
		super(Contraband, self).__init__(game, **kwargs)
		self.price = 5
		self.value = 3
		self.banning = None
	def onPlay(self, player, **kwargs):
		super(Contraband, self).onPlay(player, **kwargs)
		player.addBuy()
		self.banning = player.game.piles[list(player.game.piles)[player.game.getNextPlayer(player).user(list(player.game.piles), 'Choose ban')]]
		player.game.dp.send(signal='Choice', choice=self.banning, card=self)
		self.connect()
	def onLeavePlay(self, player, **kwargs):
		self.disconnect()
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and kwargs['pile']==self.banning: return True
	def connect(self, **kwargs):
		player.game.dp.connect(self.trigger, signal='tryBuy')
	def disconnect(self, **kwargs):
		player.game.dp.connect(self.trigger, signal='tryBuy')	
		
class CountingHouse(Action, CardAdd):
	name = 'Counting House'
	def __init__(self, game, **kwargs):
		super(CountingHouse, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(CountingHouse, self).onPlay(player, **kwargs)
		coppers = 0
		for card in player.discardPile:
			if card.name=='Copper': coppers+=1
		for i in range(player.user(list(range(coppers+1)), 'Choose amnount')):
			for n in range(len(player.discardPile)-1, -1, -1):
				if player.discardPile[n].name=='Copper': player.hand.append(player.discardPile.pop(n))
		
class Mint(Action, CardAdd):
	name = 'Mint'
	def __init__(self, game, **kwargs):
		super(Mint, self).__init__(game, **kwargs)
		self.price = 5
		game.dp.connect(self.trigger, signal='buy')
	def onPlay(self, player, **kwargs):
		super(Mint, self).onPlay(player, **kwargs)
		options = []
		for card in player.hand:
			if 'TREASURE' in card.types: optins.append(card)
		if not options: return
		choice = player.user(options+['NoMint'], 'Choose gain')
		if choice>=len(options): return
		player.gainFromPile(player.game.piles[options[choice]])
	def trigger(self, signal, **kwargs):
		if 'pile' in kwargs and not self==kwargs['pile'].viewTop(): return
		for i in range(len(kwargs['player'].inPlay)-1, -1, -1):
			if 'TREASURE' in kwargs['player'].inPlay[i].types: kwargs['player'].trashCard(kwargs['player'].getFromPlay(i))
		
class Mountebank(Action, Attack, CardAdd):
	name = 'Mountebank'
	def __init__(self, game, **kwargs):
		super(Mountebank, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Mountebank, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for aplayer in player.game.getPlayers(player):
			if not player==aplayer: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		for i in range(len(player.hand)):
			if player.hand[i].name=='Curse':
				if player.user(('keep', 'discardCurse'), ''):
					player.discard(i)
					return
				break
		player.gainFromPile(player.game.piles['Curse'])
		player.gainFromPile(player.game.piles['Copper'])

class Rabble(Action, Attack, CardAdd):
	name = 'Rabble'
	def __init__(self, game, **kwargs):
		super(Rabble, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Rabble, self).onPlay(player, **kwargs)
		player.draw(amnt=3)
		for aplayer in player.game.getPlayers(player):
			if not player==aplayer: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		cards = player.getCards(3)
		for i in range(len(cards)-1, -1, -1):
			if 'ACTION' in cards[i].types or 'TREASURE' in cards[i].types: player.discardCard(cards.pop(i))
		while cards:
			player.library.append(cards.pop(player.user([o.name for o in cards], 'Choose top')))

class Vault(Action, CardAdd):
	name = 'Vault'
	def __init__(self, game, **kwargs):
		super(Vault, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Vault, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		while player.hand:
			choice = player.user(player.hand+['EndDiscard'], 'Choose discard')
			if choice>len(player.hand): break
			player.discard(choice)
			player.addCoin()
		for aplayer in player.game.getPlayers(player):
			if len(aplayer.hand)>1 and aplayer.user(('discard', 'DoNotDiscard'), ''):
				for i in range(2): aplayer.discard(aplayer.user([o.name for o in aplayer.hand], 'Choose discard '+str(1+i)))
				aplayer.draw()

class Venture(Treasure, CardAdd):
	name = 'Venture'
	def __init__(self, game, **kwargs):
		super(Venture, self).__init__(game, **kwargs)
		self.price = 5
		self.value = 1
	def onPlay(self, player, **kwargs):
		super(Venture, self).onPlay(player, **kwargs)
		aside = []
		card = None
		treasure = None
		while True:
			card = player.getCard()
			if card=='Empty': break
			player.reveal(card)
			if 'TREASURE' in card.types:
				treasure = card
				break
			aside.append(card)
		while aside: player.discard(aside.pop())
		if treasure:
			player.inPlay.append(treasure)
			player.playTreasure(treasure)

class Goons(Action, Attack, CardAdd):
	name = 'Goons'
	def __init__(self, game, **kwargs):
		super(Goons, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 6
	def onPlay(self, player, **kwargs):
		super(Goons, self).onPlay(player, **kwargs)
		self.connect()
		player.addBuy()
		player.addCoin(amnt=2)
		for aplayer in player.game.getPlayers(player):
			if not player==aplayer: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		while len(player.hand)>3:
			choice = player.user([o.name for o in player.hand], 'Choose discard')
			player.discard(choice)		
	def onLeavePlay(self, player, **kwargs):
		self.disconnect()
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner: self.owner.addVictory()
	def connect(self, **kwargs):
		player.game.dp.connect(self.trigger, signal='buy')
	def disconnect(self, **kwargs):
		player.game.dp.connect(self.trigger, signal='buy')
		
class GrandMarket(Action, CardAdd):
	name = 'Grand Market'
	def __init__(self, game, **kwargs):
		super(GrandMarket, self).__init__(game, **kwargs)
		self.price = 6
		game.dp.connect(self.trigger, signal='tryBuy')
	def onPlay(self, player, **kwargs):
		super(GrandMarket, self).onPlay(player, **kwargs)
		player.addBuy()
		player.draw()
		player.addAction()
		player.addCoin(amnt=2)
	def trigger(self, signal, **kwargs):
		if not self==kwargs['card']: return
		for card in kwargs['player'].inPlay:
			if card.name=='Copper': return True
		
class Hoard(Treasure, CardAdd):
	name = 'Hoard'
	def __init__(self, game, **kwargs):
		super(Hoard, self).__init__(game, **kwargs)
		self.price = 6
		self.value = 2
	def onPlay(self, player, **kwargs):
		super(Hoard, self).onPlay(player, **kwargs)
		self.connect()
	def onLeavePlay(self, player, **kwargs):
		self.disconnect()
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and 'pile' in kwargs and kwargs['pile'].viewTop() and 'VICTORY' in kwargs['pile'].viewTop().types: self.owner.gainFromPile(self.owner.game.piles['Gold'])
	def connect(self, **kwargs):
		self.owner.game.dp.connect(self.trigger, signal='buy')
	def disconnect(self, **kwargs):
		self.owner.game.dp.connect(self.trigger, signal='buy')

class Bank(Treasure, CardAdd):
	name = 'Bank'
	def __init__(self, game, **kwargs):
		super(Bank, self).__init__(game, **kwargs)
		self.price = 7
	def onPlay(self, player, **kwargs):
		vsum = 0
		for card in player.inPlay:
			if 'TREASURE' in card.types: vsum+=1
		player.addCoin(amnt=vsum)
		
class Expand(Action, CardAdd):
	name = 'Expand'
	def __init__(self, game, **kwargs):
		super(Expand, self).__init__(game, **kwargs)
		self.price = 7
	def onPlay(self, player, **kwargs):
		super(Expand, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		coinVal, potionVal = player.hand[choice].getPrice(player), player.hand[choice].getPotionPrice(player)
		player.trash(choice)
		options = []
		for pile in player.game.piles:
			if player.game.piles[pile].viewTop() and player.game.piles[pile].viewTop().getPrice(player)<=coinVal+3 and player.game.piles[pile].viewTop().getPotionPrice(player)<=potionVal:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.game.piles[options[choice]])
		
class Forge(Action, CardAdd):
	name = 'Forge'
	def __init__(self, game, **kwargs):
		super(Forge, self).__init__(game, **kwargs)
		self.price = 7
	def onPlay(self, player, **kwargs):
		super(Forge, self).onPlay(player, **kwargs)
		trashedValue = 0
		while self.hand:
			choice = player.user([o.name for o in player.hand]+['EndForge'], 'Choose trash')
			if choice+1>len(player.hand): break
			trashedValue += player.hand[choice].getValue(player)
			player.trash(choice)
		options = []
		for pile in player.game.piles:
			if player.game.piles[pile].viewTop() and player.game.piles[pile].viewTop().getPrice(player)==trashedValue:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.game.piles[options[choice]])
		
class KingsCourt(Action, CardAdd):
	name = "King's Court"
	def __init__(self, game, **kwargs):
		super(KingsCourt, self).__init__(game, **kwargs)
		self.price = 7
		self.links = []
	def onPlay(self, player, **kwargs):
		super(KingsCourt, self).onPlay(player, **kwargs)
		self.links = []
		options = []
		for card in player.hand:
			if 'ACTION' in card.types:
				options.append(card)
		if not options: return
		print('\t', player.hand)
		choice = player.user([o.name for o in options], 'Choose action')
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]:
				player.inPlay.append(player.hand.pop(i))
				break
		print('\t', player.hand)
		self.links.append(options[choice])
		player.game.dp.connect(self.trigger, signal='destroy')
		for i in range(3): player.playAction(options[choice])
	def onDestroy(self, player, **kwargs):
		if self.links: return True
	def onLeavePlay(self, player, **kwargs):
		if self.links: player.game.dp.disconnect(self.trigger, signal='destroy')
	def trigger(self, signal, **kwargs):
		for i in range(len(self.links)-1, -1, -1):
			if self.links[i]==kwargs['card']: self.links.pop(i)
		if self.links: return
		for i in range(len(self.owner.inPlay)):
			if self.owner.inPlay[i]==self:
				self.owner.destroyCard(self.owner.inPlay.pop(i))
				break

class Peddler(Action, CardAdd):
	name = 'Peddler'
	def __init__(self, game, **kwargs):
		super(Peddler, self).__init__(game, **kwargs)
		self.price = 8
	def onPlay(self, player, **kwargs):
		super(Peddler, self).onPlay(player, **kwargs)
		player.addCoin()
		player.addAction()
		player.draw()
	def getPrice(self, player, **kwargs):
		isBuy = False
		for i in range(len(player.game.events)-1, -1, -1):
			if player.game.events[i][0]=='actionPhase' or player.game.events[i][0]=='treasurePhase': break
			elif player.game.events[i][0]=='buyPhase':
				isBuy = player.game.events[i][1]['player']==player
				break
		if not isBuy: return np.max((self.price, 0))
		actions = 0
		for card in player.inPlay:
			if 'ACTION' in card.types: actions+=1
		return np.max((self.price-actions*2, 0))
		
prosperity = [Loan, TradeRoute, Watchtower, Bishop, Monument, Quarry, Talisman, WorkersVillage, City, Contraband, CountingHouse, Mint, Mountebank, Rabble, Vault, Venture, Goons, GrandMarket, Hoard, Bank, Expand, Forge, KingsCourt, Peddler]

class Colony(Victory, CardAdd):
	name = 'Colony'
	def __init__(self, game, **kwargs):
		super(Colony, self).__init__(game, **kwargs)
		self.value = 10
		self.price = 11
	def onPileCreate(self, pile, game, **kwargs):
		pile.terminator = True
		if len(game.players)>3:
			amnt = 12
		else:
			amnt = 8
		for i in range(amnt):
			pile.append(type(self)(game))
			
class Platinum(Treasure, CardAdd):
	name = 'Platinum'
	def __init__(self, game, **kwargs):
		super(Platinum, self).__init__(game, **kwargs)
		self.value = 5
		self.price = 9
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(12):
			pile.append(type(self)(game))
			
platColony = [Colony, Platinum]

class EmbargoToken(Token):
	name = 'Embargo Token'
	def __init__(self, game, **kwargs):
		super(EmbargoToken, self).__init__(game, **kwargs)
		game.dp.connect(self.trigger, signal='buy')
	def trigger(self, signal, **kwargs):
		if kwargs['pile']==self.owner:
			print('EMBARGO', kwargs['player'])
			kwargs['player'].gainFromPile(player.game.piles['Curse'])
						
class Embargo(Action, CardAdd):
	name = 'Embargo'
	def __init__(self, game, **kwargs):
		super(Embargo, self).__init__(game, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Embargo, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.trashCard(player.getFromPlay(i))
				break
		player.game.piles[list(player.game.piles)[player.user(list(player.game.piles), 'Choose embargo')]].addToken(EmbargoToken(player.game), player.game)
	
class Haven(Action, Duration, CardAdd):
	name = 'Haven'
	def __init__(self, game, **kwargs):
		super(Haven, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 2
		self.saved = []
	def onPlay(self, player, **kwargs):
		super(Haven, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		self.age = 0
		player.game.dp.connect(self.nextage, signal='startTurn')
		if not player.hand: return
		self.saved.append(player.hand.pop(player.user([o.name for o in player.hand], 'Choose saved')))
	def nextage(self, signal, **kwargs):
		if kwargs['player']==self.owner:
			self.age+=1
			while self.saved: self.owner.hand.append(self.saved.pop())
	def onGameEnd(self, player, **kwargs):
		while self.saved: player.library.append(self.saved.pop())
			
class Lighthouse(Action, Duration, CardAdd):
	name = 'Lighthouse'
	def __init__(self, game, **kwargs):
		super(Lighthouse, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Lighthouse, self).onPlay(player, **kwargs)
		player.addAction()
		player.addCoin()
		self.age = 0
		player.game.dp.connect(self.nextage)
	def nextage(self, signal, **kwargs):
		if signal=='startTurn' and kwargs['player']==self.owner:
			self.age+=1
			self.owner.addCoin()
		elif signal=='attack' and kwargs['player']==self.owner: return True

class NativeVillage(Action, CardAdd):
	name = 'Native Village'
	def __init__(self, game, **kwargs):
		super(NativeVillage, self).__init__(game, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(NativeVillage, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		if player.user(('takeCards', 'addCard'), ''):
			topCard = player.getCard()
			player.mats['NativeVillageMat'].append(topCard)
			player.reveal(topCard, hidden=player)
		else:
			while player.mats['NativeVillageMat']: player.hand.append(player.mats['NativeVillageMat'].pop())
	def onPileCreate(self, pile, game, **kwargs):
		super(NativeVillage, self).onPileCreate(pile, game, **kwargs)
		game.addMat('NativeVillageMat')

class PearlDiver(Action, CardAdd):
	name = 'Pearl Diver'
	def __init__(self, game, **kwargs):
		super(PearlDiver, self).__init__(game, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(PearlDiver, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
		if not player.library: return
		player.reveal(player.library[0], hidden=player)
		if not player.user(('top', 'bot'), ''): player.library.append(player.library.pop(0))

class Ambassador(Action, Attack, CardAdd):
	name = 'Ambassador'
	def __init__(self, game, **kwargs):
		super(Ambassador, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Ambassador, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose return')
		revealedCard = player.hand[choice]
		player.reveal(revealedCard)
		if not revealedCard.name in player.game.piles: return
		amnt = player.user(list(range(3)), 'Choose return amount')
		returned = 0
		for i in range(len(player.hand)-1, -1, -1):
			if returned==amnt: break
			if player.hand[i].name==revealedCard.name:
				player.returnCard(player.hand.pop(i))
				returned+=1
		for aplayer in player.game.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self, pile=player.game.piles[revealedCard.name])
	def attack(self, player, **kwargs):
		player.gainFromPile(kwargs['pile'])
		
class FishingVillage(Action, Duration, CardAdd):
	name = 'Fishing Village'
	def __init__(self, game, **kwargs):
		super(FishingVillage, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 3
		self.nexts = []
	def onPlay(self, player, **kwargs):
		super(FishingVillage, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		player.addCoin()
	def next(self, **kwargs):
		self.owner.addAction()
		self.owner.addCoin()

class Lookout(Action, CardAdd):
	name = 'Lookout'
	def __init__(self, game, **kwargs):
		super(Lookout, self).__init__(game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Lookout, self).onPlay(player, **kwargs)
		player.addAction()
		cards = player.getCards(3)
		if not cards: return
		player.trashCard(cards.pop(player.user([o.name for o in cards], 'Choose trash')))
		if not cards: return
		player.discardCard(cards.pop(player.user([o.name for o in cards], 'Choose discard')))
		if not cards: return
		while cards: player.library.append(cards.pop())

class Smugglers(Action, CardAdd):
	name = 'Smugglers'
	def __init__(self, game, **kwargs):
		super(Smugglers, self).__init__(game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Smugglers, self).onPlay(player, **kwargs)
		previousPlayer = player.game.getPreviousPlayer(player)
		options = []
		for i in range(len(events)-1, -1, -1):
			if events[i][0]=='startTurn' and events[i][1]['player']==previousPlayer:
				for n in range(i, len(events)):
					if events[n][0]=='gain' and events[n][1]['player']==previousPlayer and events[n][1]['card'].getPrice(player)<7: options.append(events[n][1]['card'].name)
					elif events[n][0]=='endTurn': break
				break
		if not options: return
		player.gainFromPile(player.game.piles[options[player.user(options, 'Choose smuggle')]])
					
class Warehouse(Action, CardAdd):
	name = 'Warehouse'
	def __init__(self, game, **kwargs):
		super(Warehouse, self).__init__(game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Warehouse, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw(amnt=3)
		for i in range(3):
			if not player.hand: return
			player.discard(player.user([o.name for o in player.hand], 'Discard card'+str(1+i)))
			
class Caravan(Action, Duration, CardAdd):
	name = 'Caravan'
	def __init__(self, game, **kwargs):
		super(Caravan, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Caravan, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
	def next(self, **kwargs):
		self.owner.draw()
		
class Cutpurse(Action, CardAdd):
	name = 'Cutpurse'
	def __init__(self, game, **kwargs):
		super(Cutpurse, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Cutpurse, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for aplayer in player.game.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		for i in range(len(player.hand)):
			if player.hand[i].name=='Copper':
				player.discard(i)
				return
		for card in player.hand:
			player.reveal(card)
		
class Island(Action, Victory, CardAdd):
	name = 'Island'
	def __init__(self, game, **kwargs):
		super(Island, self).__init__(game, **kwargs)
		Victory.__init__(self, game, **kwargs)
		self.price = 4
		self.value = 2
	def onPlay(self, player, **kwargs):
		super(Island, self).onPlay(player, **kwargs)
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self: player.mats['IslandMat'].append(player.getFromPlay(i))
		if not player.hand: return
		player.mats['IslandMat'].append(player.hand.pop(player.user([o.name for o in player.hand], 'Choose hide')))
	def onPileCreate(self, pile, game, **kwargs):
		super(Island, self).onPileCreate(pile, game, **kwargs)
		game.addMat('IslandMat')
		
class Navigator(Action, CardAdd):
	name = 'Navigator'
	def __init__(self, game, **kwargs):
		super(Navigator, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Navigator, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		cards = player.getCards(5)
		if not cards: return
		for card in cards: player.reveal(card, hidden=player)
		if player.user(('top', 'discard'), ''):
			while cards: player.discardCard(cards.pop())
		else:
			while cards: player.library.append(cards.pop(player.user([o.name for o in cards], 'Choose top order')))
		
class PirateToken(Token): pass
		
class PirateShip(Action, Attack, CardAdd):
	name = 'Pirate Ship'
	def __init__(self, game, **kwargs):
		super(PirateShip, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(PirateShip, self).onPlay(player, **kwargs)
		if player.user(('attack', 'money'), ''): player.addCoin(amnt=len(player.mats['PirateMat']))
		else:
			for aplayer in player.game.getPlayers(player):
				if not player==aplayer: aplayer.attack(self.attack, self)
	def onPileCreate(self, pile, game, **kwargs):
		super(PirateShip, self).onPileCreate(pile, game, **kwargs)
		game.addMat('PirateMat')
	def attack(self, player, **kwargs):
		cards = player.getCards(2)
		if not cards: return
		options = []
		for card in cards:
			player.reveal(card)
			if 'TREASURE' in card.types: options.append(card)
		if options:
			choice = self.owner.user([o.name for o in options], 'Choose trash')
			for i in range(len(cards)):
				if cards[i]==options[choice]:
					player.trashCard(cards.pop(i))
					self.owner.mats['PirateMat'].append(PirateToken())
					break
		while cards: player.discardCard(cards.pop())
		
class Salvager(Action, CardAdd):
	name = 'Salvager'
	def __init__(self, game, **kwargs):
		super(Salvager, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Salvager, self).onPlay(player, **kwargs)
		player.addBuy()
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		player.addCoin(amnt=player.hand[choice].getPrice(player))
		player.trash(choice)
		
class SeaHag(Action, Attack, CardAdd):
	name = 'Sea Hag'
	def __init__(self, game, **kwargs):
		super(SeaHag, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(SeaHag, self).onPlay(player, **kwargs)
		for aplayer in player.game.getPlayers(player):
			if not player==aplayer: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		player.discardCard(player.getCard())
		player.gainFromPile(player.game.piles['Curse'], to=player.library)
		
class TreasureMap(Action, CardAdd):
	name = 'Treasure Map'
	def __init__(self, game, **kwargs):
		super(TreasureMap, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(TreasureMap, self).onPlay(player, **kwargs)
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.trashCard(player.getFromPlay(i))
				break
		for i in range(len(player.hand)):
			if player.hand[i].name=='Treasure Map':
				player.trash(i)
				for n in range(4): player.gainFromPile(player.game.piles['Gold'], to=player.library)
				return
		
class Bazaar(Action, CardAdd):
	name = 'Bazaar'
	def __init__(self, game, **kwargs):
		super(Bazaar, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Bazaar, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		player.draw()
		player.addCoin()
		
class Explorer(Action, CardAdd):
	name = 'Explorer'
	def __init__(self, game, **kwargs):
		super(Explorer, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Explorer, self).onPlay(player, **kwargs)
		if player.hand and player.user(('no', 'revealProvince'), ''):
			for card in player.hand:
				if card.name=='Province':
					player.gainFromPile(player.game.piles['Gold'], to=player.hand)
					return
		player.gainFromPile(player.game.piles['Silver'], to=player.hand)
		
class GhostShip(Action, Attack, CardAdd):
	name = 'Ghost Ship'
	def __init__(self, game, **kwargs):
		super(GhostShip, self).__init__(game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(GhostShip, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		for aplayer in player.game.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		while len(player.hand)>3:
			choice = player.user([o.name for o in player.hand], 'Choose top')
			player.library.append(player.hand.pop(choice))
		
class MerchantShip(Action, Duration, CardAdd):
	name = 'Merchant Ship'
	def __init__(self, game, **kwargs):
		super(MerchantShip, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(MerchantShip, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
	def next(self, **kwargs):
		self.owner.addCoin(amnt=2)
		
class Tactician(Action, Duration, CardAdd):
	name = 'Tactician'
	def __init__(self, game, **kwargs):
		super(Tactician, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Tactician, self).onPlay(player, **kwargs)
		player.game.dp.connect(self.trigger, signal='startTurn')
		self.age = 0
		if not player.hand: return
		player.discardHand()
		self.nexts.append(self.next)
	def next(self, **kwargs):
		self.owner.draw(amnt=5)
		self.owner.addBuy()
		self.owner.addAction()
		
class Treasury(Action, CardAdd):
	name = 'Treasury'
	def __init__(self, game, **kwargs):
		super(Treasury, self).__init__(game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Treasury, self).onPlay(player, **kwargs)
		player.addAction()
		player.addCoin()
		player.draw()
	def onDestroy(self, player, **kwargs):
		for i in range(len(events)-1, -1, -1):
			if events[0]=='buy' and events[1]['card'] and 'VICTORY' in events[1]['card'].types: return
			elif events[0]=='startTurn': break
		if not player.user(('bot', 'top')): return
		print(player.inPlay)
		for i in range(len(player.inPlay)):
			print(i, player.inPlay[i], self)
			if player.inPlay[i]==self: player.library.append(player.inPlay.pop(i))
			return True

class Outpost(Action, Duration, CardAdd):
	name = 'Outpost'
	def __init__(self, game, **kwargs):
		super(Outpost, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Outpost, self).onPlay(player, **kwargs)
		player.eotdraw = 3
		print(player.eotdraw)
		player.game.delayedActions.append((self.outpostTurn, {'player': player}))
	def outpostTurn(self, **kwargs):
		turns = 0
		for i in range(len(kwargs['player'].game.events)-1, -1, -1):
			if kwargs['player'].game.events[0]=='startTurn':
				if kwargs['player'].game.event[1]['player']==self: turns+=1
				else: break
		if turns>1: return
		kwargs['player'].game.activePlayer = self
		kwargs['player'].game.turnFlag = 'outpost'
		kwargs['player'].resetValues()
		kwargs['player'].game.dp.send(signal='startTurn', player=self)
		kwargs['player'].actionPhase()
		kwargs['player'].treasurePhase()
		kwargs['player'].buyPhase()
		kwargs['player'].endTurn()
			
seaside = [Embargo, Haven, Lighthouse, NativeVillage, Ambassador, FishingVillage, Lookout, Smugglers, Caravan, Cutpurse, Island, Navigator, PirateShip, Salvager, SeaHag, TreasureMap, Bazaar, Explorer, GhostShip, MerchantShip, Outpost, Tactician, Treasury]

class BoonToken(Token):
	name = 'Base Boon Token'
	def __init__(self, game, **kwargs):
		super(PlusCard, self).__init__(game, **kwargs)
		self.playerOwner = None
		self.types.append('BOONTOKEN')
	def trigger(self, signal, **kwargs):
		if kwargs['card'].name==self.owner.cardType.name and kwargs['player']==self.playerOwner: self.boon(self.playerOwner)
	def boon(self, player, **kwargs):
		pass
	def onAddPile(self, pile, **kwargs):
		pile.game.dp.connect(self.trigger, signal='playAction')
	def onLeavePile(self, pile, **kwargs):
		pile.game.dp.diccnnect(self.trigger, signal='playAction')

class PlusCard(BoonToken):
	name = 'PlusCard'
	def boon(self, player, **kwargs):
		player.draw()
		
class CoinOfTheRealm(Treasure, Reserve, CardAdd):
	name = 'Coin of the Realm'
	def __init__(self, game, **kwargs):
		super(CoinOfTheRealm, self).__init__(game, **kwargs)
		Reserve.__init__(self, game, **kwargs)
		self.triggerSignal = 'playAction'
		self.value = 1
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(CoinOfTheRealm, self).onPlay(player, **kwargs)
		Reserve.onPlay(self, player, **kwargs)
	def call(self, signal, **kwargs):
		super(CoinOfTheRealm, self).call(signal, **kwargs)
		self.owner.addAction(amnt=2)
		
class Page(Action, Traveler, CardAdd):
	name = 'Page'
	def __init__(self, game, **kwargs):
		super(Page, self).__init__(game, **kwargs)
		Traveler.__init__(self, game, **kwargs)
		self.morph = TreasureHunter 
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Page, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.draw()
		player.addAction()
		
class TreasureHunter(Action, Traveler, CardAdd):
	name = 'Treasure Hunter'
	def __init__(self, game, **kwargs):
		super(TreasureHunter, self).__init__(game, **kwargs)
		Traveler.__init__(self, game, **kwargs)
		self.morph = Warrior 
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(TreasureHunter, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.addCoin()
		player.addAction()
		previousPlayer = None
		for i in range(len(player.game.events)-1, -1, -1):
			if player.game.events[i][0]=='startTurn' and player.game.events[i][1]['player']!=player:
				previousPlayer = player.game.events[i][1]['player']
				for n in range(i, len(player.game.events)):
					if player.game.events[n][0]=='gain' and player.game.events[n][1]['player']==previousPlayer: player.gainFromPile(player.game.piles['Silver'])
					elif player.game.events[n][0]=='endTurn': return
	def onPileCreate(self, pile, game, **kwargs):
		game.require(self.morph)
		for i in range(5): pile.append(type(self)(game))
				
class Warrior(Action, Traveler, Attack, CardAdd):
	name = 'Warrior'
	def __init__(self, game, **kwargs):
		super(Warrior, self).__init__(game, **kwargs)
		Traveler.__init__(self, game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.morph = Hero 
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Warrior, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.draw(amnt=2)
		travelers = 0
		for card in player.inPlay:
			if 'TRAVELER' in card.types: travelers += 1
		for aplayer in player.game.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self, amnt=travelers)
	def attack(self, player, **kwargs):
		for i in range(kwargs['amnt']):
			card = player.getCard()
			if not card: break
			player.discardCard(card)
			if not (card.getPrice(player) in (3, 4) and card.getPotionPrice(player)==0): continue
			for i in range(len(player.discardPile)-1, -1, -1):
				if player.discardPile[i]==card: player.trashCard(player.discardPile.pop(i))
	def onPileCreate(self, pile, game, **kwargs):
		game.require(self.morph)
		for i in range(5): pile.append(type(self)(game))
				
class Hero(Action, Traveler, CardAdd):
	name = 'Hero'
	def __init__(self, game, **kwargs):
		super(Hero, self).__init__(game, **kwargs)
		Traveler.__init__(self, game, **kwargs)
		self.morph = Champion 
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Hero, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		options = []
		for pile in player.game.piles:
			if player.game.piles[pile].viewTop() and 'TREASURE' in player.game.piles[pile].viewTop().types: options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.game.piles[options[choice]])
	def onPileCreate(self, pile, game, **kwargs):
		game.require(self.morph)
		for i in range(5): pile.append(type(self)(game))
		
class Champion(Action, Duration, CardAdd):
	name = 'Champion'
	def __init__(self, game, **kwargs):
		super(Champion, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 6
	def onPlay(self, player, **kwargs):
		player.addAction()
		player.game.dp.connect(self.defence, signal='attack')
		player.game.dp.connect(self.addAction, signal='playAction')
	def defence(self, signal, **kwargs):
		if kwargs['player']==self.owner: return True
	def addAction(self, signal, **kwargs):
		if kwargs['player']==self.owner: self.owner.addAction()
	def onLeavePlay(self, player, **kwargs):
		pass
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(5): pile.append(type(self)(game))
		
class Peasant(Action, Traveler, CardAdd):
	name = 'Peasant'
	def __init__(self, game, **kwargs):
		super(Peasant, self).__init__(game, **kwargs)
		Traveler.__init__(self, game, **kwargs)
		self.morph = Soldier 
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Peasant).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.addCoin()
		player.addBuy()

class Soldier(Action, Traveler, Attack, CardAdd):
	name = 'Soldier'
	def __init__(self, game, **kwargs):
		super(Soldier, self).__init__(game, **kwargs)
		Traveler.__init__(self, game, **kwargs)
		Attack.__init__(self, game, **kwargs)
		self.morph = Figitive 
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Soldier, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.addCoin(amnt=2)
		attacks = 0
		for card in player.inPlay:
			if 'ATTACK' in card.types and card==self: attacks += 1
		player.addCoin(amnt=attacks)
		for aplayer in player.game.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		if len(player.hand)>3: player.discard(player.user([o.name for o in player.hand], 'Choose discard'))
	def onPileCreate(self, pile, game, **kwargs):
		game.require(self.morph)
		for i in range(5): pile.append(type(self)(game))
		
class Fugitive(Action, Traveler, CardAdd):
	name = 'Fugitive'
	def __init__(self, game, **kwargs):
		super(Fugitive, self).__init__(game, **kwargs)
		Traveler.__init__(self, game, **kwargs)
		self.morph = Disciple 
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Fugitive, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.draw(amnt=2)
		player.addAction()
		if player.hand: player.discard(player.user([o.name for o in player.hand], 'Choose discard'))
	def onPileCreate(self, pile, game, **kwargs):
		game.require(self.morph)
		for i in range(5): pile.append(type(self)(game))
		
class Disciple(Action, Traveler, CardAdd):
	name = 'Disciple'
	def __init__(self, game, **kwargs):
		super(Disciple, self).__init__(game, **kwargs)
		Traveler.__init__(self, game, **kwargs)
		self.morph = Teacher 
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Disciple, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		self.links = []
		options = []
		for card in player.hand:
			if 'ACTION' in card.types:
				options.append(card)
		if not options: return
		choice = player.user([o.name for o in options]+'Play no action', 'Choose action')
		if choice+1>len(options): return
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]:
				player.inPlay.append(player.hand.pop(i))
				break
		self.links.append(options[choice])
		player.game.dp.connect(self.trigger, signal='destroy')
		for i in range(2): player.playAction(options[choice])
		if options[choice].name in list(player.game.piles): player.gainFromPile(player.game.piles[options[choice].name])
	def onDestroy(self, player, **kwargs):
		if self.links: return True
	def onLeavePlay(self, player, **kwargs):
		if self.links: player.game.dp.disconnect(self.trigger, signal='destroy')
	def trigger(self, signal, **kwargs):
		for i in range(len(self.links)-1, -1, -1):
			if self.links[i]==kwargs['card']: self.links.pop(i)
		if self.links: return
		for i in range(len(self.owner.inPlay)):
			if self.owner.inPlay[i]==self:
				self.owner.destroyCard(self.owner.inPlay.pop(i))
				break
	def onPileCreate(self, pile, game, **kwargs):
		game.require(self.morph)
		for i in range(5): pile.append(type(self)(game))

class Teacher(Action, Reserve, CardAdd):
	name = 'Teacher'
	def __init__(self, game, **kwargs):
		super(Teacher).__init__(game, **kwargs)
		Reserve.__init__(self, game, **kwargs)
		self.triggerSignal = 'startTurn'
		self.price = 6
	def onPlay(self, player, **kwargs):
		super(Teacher, self).onPlay(player, **kwargs)
	def call(self, signal, **kwargs):
		super(Teacher, self).call(signal, **kwargs)

class Ratcatcher(Action, Reserve, CardAdd):
	name = 'Ratcatcher'
	def __init__(self, game, **kwargs):
		super(Ratcatcher, self).__init__(game, **kwargs)
		self.triggerSignal = 'startTurn'
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Ratcatcher, self).onPlay(player, **kwargs)
		Reserve.onPlay(self, player, **kwargs)
		player.addAction()
		player.draw()
	def call(self, signal, **kwargs):
		if not self.owner.hand: return
		super(Ratcatcher, self).call(signal, **kwargs)
		self.owner.trash(self.owner.user([o.name for o in self.owner.hand], 'Choose trash'))
		
class Raze(Action, CardAdd):
	name = 'Raze'
	def __init__(self, game, **kwargs):
		super(Raze, self).__init__(game, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Raze, self).onPlay(player, **kwargs)
		player.addAction()
		choice = player.user([o.name for o in player.hand]+['Raze itself'], 'Choose action')
		if choice+1>len(player.hand):
			trashedPrice = self.getPrice(player)
			for i in range(len(player.inPlay)):
				if player.inPlay[i]==self: player.trashCard(player.inPlay.pop(i))
		else:
			trashedPrice = player.hand[choice].getPrice(player)
			player.trash(choice)
		if not trashedPrice: return
		cards = player.getCards(trashedPrice)
		if not cards: return
		player.hand.append(cards.pop(player.user([o.name for o in cards], 'Choose card')))
		while cards: player.discardCard(cards.pop())
			
class Amulet(Action, Duration, CardAdd):
	name = 'Amulet'
	def __init__(self, game, **kwargs):
		super(Amulet, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Amulet, self).onPlay(player, **kwargs)
		self.next()
	def next(self, **kwargs):
		choice = self.owner.user(('+1 coin', 'Trash card', 'Gain silver'), 'Choose one')
		if choice==0: self.owner.addCoin()
		elif choice==1:
			if not self.owner.hand: return
			self.owner.trash(self.owner.user([o.name for o in self.owner.hand], 'Choose trash'))
		elif choice==2: self.owner.gainFromPile(self.owner.game.piles['Silver'])
			
class CaravanGuard(Action, Duration, Reaction, CardAdd):
	name = 'Caravan Guard'
	def __init__(self, game, **kwargs):
		super(CaravanGuard, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		Reaction.__init__(self, game, **kwargs)
		self.price = 3
		self.signal = 'Attack'
	def onPlay(self, player, **kwargs):
		super(CaravanGuard, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
	def next(self, **kwargs):
		self.owner.addCoin()
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and self in self.owner.hand and self.owner.user(('no', 'yes'), 'Use Caravan Guard'):
			for i in range(len(self.owner.hand)):
				if self==self.owner.hand[i]:
					self.owner.inPlay.append(self.owner,hand.pop(i))
					self.owner.playAction(self)
					break
	def connect(self, **kwargs):
		kwargs['player'].game.dp.connect(self.trigger, signal=self.signal)
	def disconnect(self, **kwargs):
		kwargs['player'].game.dp.connect(self.trigger, signal=self.signal)
	def onGain(self, player, **kwargs):
		self.connect(player=player)
	def onTrash(self, player, **kwargs):
		self.disconnect(player=player)
	def onReturn(self, player, **kwargs):
		self.disconnect(player=player)

class Dungeon(Action, Duration, CardAdd):
	name = 'Dungeon'
	def __init__(self, game, **kwargs):
		super(Dungeon, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Dungeon, self).onPlay(player, **kwargs)
		player.addAction()
		self.next()
	def next(self, **kwargs):
		self.owner.draw(amnt=2)
		for i in range(2):
			if not self.owner.hand: break
			self.owner.discard(self.owner.user([o.name for o in self.owner.hand], 'Choose discard '+str(i+1)))

class Gear(Action, Duration, CardAdd):
	name = 'Gear'
	def __init__(self, game, **kwargs):
		super(Gear, self).__init__(game, **kwargs)
		Duration.__init__(self, game, **kwargs)
		self.price = 3
		self.saved = []
	def onPlay(self, player, **kwargs):
		super(Gear, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		self.age = 0
		player.game.dp.connect(self.trigger, signal='startTurn')
		for i in range(2):
			if not player.hand: return
			self.saved.append(player.hand.pop(player.user([o.name for o in player.hand], 'Choose saved '+str(i+1))))
	def nextage(self, signal, **kwargs):
		if kwargs['player']==self.owner:
			self.age+=1
			while self.saved: self.owner.hand.append(self.saved.pop())
	def onGameEnd(self, player, **kwargs):
		while self.saved: player.library.append(self.saved.pop())
			
class Guide(Action, Reserve, CardAdd):
	name = 'Guide'
	def __init__(self, game, **kwargs):
		super(Guide, self).__init__(game, **kwargs)
		Reserve.__init__(self, game, **kwargs)
		self.triggerSignal = 'startTurn'
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Guide, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
	def call(self, signal, **kwargs):
		super(Guide, self).call(signal, **kwargs)
		while self.owner.hand: self.owner.discardCard(self.owner.hand.pop())
		self.owner.draw(amnt=5)
			
class Duplicate(Action, Reserve, CardAdd):
	name = 'Duplicate'
	def __init__(self, game, **kwargs):
		super(Duplicate, self).__init__(game, **kwargs)
		self.triggerSignal = 'gain'
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Duplicate, self).onPlay(player, **kwargs)
		Reserve.onPlay(self, player, **kwargs)
	def requirements(self, **kwargs):
		return self.owner==kwargs['player'] and kwargs['card'].getPrice(self.owner)<7 and kwargs['card'].name in list(self.owner.game.piles)
	def call(self, signal, **kwargs):
		super(Duplicate, self).call(signal, **kwargs)
		self.owner.gainFromPile(self.owner.game.piles[kwargs['card'].name])
			
class Magpie(Action, CardAdd):
	name = 'Magpie'
	def __init__(self, game, **kwargs):
		super(Magpie, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Magpie, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		revealedCard = player.revealPosition(-1, fromZ=player.library)
		if 'TREASURE' in revealedCard.types: player.draw()
		if 'ACTION' in revealedCard.types or 'VICTORY' in revealedCard.types: player.gainFromPile(player.game.piles['Magpie'])

class Messenger(Action, CardAdd):
	name = 'Messenger'
	def __init__(self, game, **kwargs):
		super(Messenger, self).__init__(game, **kwargs)
		self.price = 4
		game.dp.connect(self.trigger, signal='buy')
	def onPlay(self, player, **kwargs):
		super(Messenger, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		player.addBuy()
		if player.user(('no', 'yes'), 'Discard library'):
			player.game.dp.send(signal='Announce', message='Discard deck')
			while player.library:
				player.discardPile.append(player.library.pop())
	def trigger(self, signal, **kwargs):
		if not self==kwargs['card']: return
		for i in range(len(kwargs['player'].game.events)-1, -1, -1):
			if kwargs['player'].game.events[i][0]=='buy' and kwargs['player'].game.events[i][1]['card']!=self: return
			elif kwargs['player'].game.events[i][0]=='startTurn': break
		options = []
		for pile in kwargs['player'].game.piles:
			if kwargs['player'].game.piles[pile].viewTop() and kwargs['player'].game.piles[pile].viewTop().getPrice(kwargs['player'])<5 and kwargs['player'].game.piles[pile].viewTop().getPotionPrice(kwargs['player'])<1: options.append(pile)
		if not options: return
		choice = kwargs['player'].user(options, 'Choose gain')
		for player in kwargs['player'].game.getPlayer(kwargs['player']): player.gainFromPile(kwargs['player'].game.piles[options[choice]])

class Miser(Action, CardAdd):
	name = 'Miser'
	def __init__(self, game, **kwargs):
		super(Miser, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Miser, self).onPlay(player, **kwargs)
		if player.user(('Coins', 'Hidde Copper'), 'Choose mode'):
			for i in range(len(player.hand)):
				if player.hand[i].name=='Copper':
					player.mats['Tavern'].append(player.hand.pop(i))
					break
		else:
			coppers = 0
			for card in player.mats['Tavern']:
				if card.name=='Copper': coppers += 1
			player.addCoin(amnt=coppers)
	def onPileCreate(self, pile, game, **kwargs):
		super(Miser, self).onPileCreate(pile, game, **kwargs)
		game.addMat('Tavern')
	
class Port(Action, CardAdd):
	name = 'Port'
	def __init__(self, game, **kwargs):
		super(Port, self).__init__(game, **kwargs)
		self.price = 4
		game.dp.connect(self.trigger, signal='buy')
	def onPlay(self, player, **kwargs):
		super(Port, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		player.draw()
	def trigger(self, signal, **kwargs):
		if 'pile' in kwargs and not self==kwargs['pile'].viewTop(): return
		kwargs['player'].gainFromPile(kwargs['player'].game.piles['Port'])
	def onPileCreate(self, pile, game, **kwargs):
		for i in range(12):
			pile.append(type(self)(game))

class Ranger(Action, CardAdd):
	name = 'Ranger'
	def __init__(self, game, **kwargs):
		super(Ranger, self).__init__(game, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Ranger, self).onPlay(player, **kwargs)
		player.addBuy()
		if player.flipJourney(): player.draw(amnt=5)

		
adventures = [CoinOfTheRealm, Page, Ratcatcher, Raze, Amulet, CaravanGuard, Dungeon, Gear, Guide, Duplicate, Magpie, Messenger, Miser, Port, Ranger]