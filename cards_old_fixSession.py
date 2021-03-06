from dombase import *

class Copper(Treasure, CardAdd):
	name = 'Copper'
	def __init__(self, session, **kwargs):
		super(Copper, self).__init__(session, **kwargs)
		self.value = 1
		self.price = 0
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(60-len(session.players)*7):
			pile.append(type(self)(session))

class Silver(Treasure, CardAdd):
	name = 'Silver'
	def __init__(self, session, **kwargs):
		super(Silver, self).__init__(session, **kwargs)
		self.value = 2
		self.price = 3
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(40):
			pile.append(type(self)(session))
		
class Gold(Treasure, CardAdd):
	name = 'Gold'
	def __init__(self, session, **kwargs):
		super(Gold, self).__init__(session, **kwargs)
		self.value = 3
		self.price = 6
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(30):
			pile.append(type(self)(session))
		
class Estate(Victory, CardAdd):
	name = 'Estate'
	def __init__(self, session, **kwargs):
		super(Estate, self).__init__(session, **kwargs)
		self.value = 1
		self.price = 2
	def onPileCreate(self, pile, session, **kwargs):
		if len(session.players)>2:
			amnt = 12
		else:
			amnt = 8
		for i in range(amnt+len(session.players)*3):
			pile.append(type(self)(session))

class Duchy(Victory, CardAdd):
	name = 'Duchy'
	def __init__(self, session, **kwargs):
		super(Duchy, self).__init__(session, **kwargs)
		self.value = 3
		self.price = 5

class Province(Victory, CardAdd):
	name = 'Province'
	def __init__(self, session, **kwargs):
		super(Province, self).__init__(session, **kwargs)
		self.value = 6
		self.price = 8
	def onPileCreate(self, pile, session, **kwargs):
		super(Province, self).onPileCreate(pile, session)
		pile.terminator = True
		
class Curse(Cursed, CardAdd):
	name = 'Curse'
	def __init__(self, session, **kwargs):
		super(Curse, self).__init__(session, **kwargs)
		self.value = -1
		self.price = 0
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(10*np.max((len(session.players)-1, 1))):
			pile.append(type(self)(session))
		
baseSetBase = [Copper, Silver, Gold, Estate, Duchy, Province, Curse]

class Cellar(Action, CardAdd):
	name = 'Cellar'
	def __init__(self, session, **kwargs):
		super(Cellar, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Chapel, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Moat, self).__init__(session, **kwargs)
		Reaction.__init__(self, session, **kwargs)
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
		kwargs['player'].session.dp.connect(self.trigger, signal=self.signal)
	def disconnect(self, **kwargs):
		kwargs['player'].session.dp.disconnect(self.trigger, signal=self.signal)
	def onGain(self, player, **kwargs):
		self.connect(player=player)
	def onTrash(self, player, **kwargs):
		self.disconnect(player=player)
	def onReturn(self, player, **kwargs):
		self.disconnect(player=player)
		
class Chancellor(Action, CardAdd):
	name = 'Chancellor'
	def __init__(self, session, **kwargs):
		super(Chancellor, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Chancellor, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		if player.user(('no', 'yes'), 'Discard library'):
			player.session.dp.send(signal='Announce', message='Discard deck')
			while player.library:
				player.discardPile.append(player.library.pop())
		
class Village(Action, CardAdd):
	name = 'Village'
	def __init__(self, session, **kwargs):
		super(Village, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Village, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction(amnt=2)
		
class Woodcutter(Action, CardAdd):
	name = 'Woodcutter'
	def __init__(self, session, **kwargs):
		super(Woodcutter, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Woodcutter, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		player.addBuy()
		
class Workshop(Action, CardAdd):
	name = 'Workshop'
	def __init__(self, session, **kwargs):
		super(Workshop, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Workshop, self).onPlay(player, **kwargs)
		options = []
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and player.session.piles[pile].viewTop().getPrice(player)<5 and player.session.piles[pile].viewTop().getPotionPrice(player)<1 and player.session.piles[pile].viewTop().getDebtPrice(player)<1:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.session.piles[options[choice]])
		
class Bureaucrat(Action, Attack, CardAdd):
	name = 'Bureaucrat'
	def __init__(self, session, **kwargs):
		super(Bureaucrat, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Bureaucrat, self).onPlay(player, **kwargs)
		player.gainFromPile(player.session.piles['Silver'], to=player.library)
		for aplayer in player.session.getPlayers(player):
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
	def __init__(self, session, **kwargs):
		super(Feast, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Feast, self).onPlay(player, **kwargs)
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.trashCard(player.getFromPlay(i))
				break
		options = []
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and player.session.piles[pile].viewTop().getPrice(player)<6 and player.session.piles[pile].viewTop().getPotionPrice(player)<1 and player.session.piles[pile].viewTop().getDebtPrice(player)<1:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.session.piles[options[choice]])
		
class Gardens(Victory, CardAdd):
	name = 'Gardens'
	def __init__(self, session, **kwargs):
		super(Gardens, self).__init__(session, **kwargs)
		self.price = 4
	def onGameEnd(self, player, **kwargs):
		player.addVictory(amnt=m.floor(len(player.library)/10))
	
class Militia(Action, Attack, CardAdd):
	name = 'Militia'
	def __init__(self, session, **kwargs):
		super(Militia, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Militia, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for aplayer in player.session.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		while len(player.hand)>3:
			choice = player.user([o.name for o in player.hand], 'Choose discard')
			player.discard(choice)

class Moneylender(Action, CardAdd):
	name = 'Moneylender'
	def __init__(self, session, **kwargs):
		super(Moneylender, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Remodel, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Remodel, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		coinVal, potionVal, debtPrice = player.hand[choice].getPrice(player), player.hand[choice].getPotionPrice(player), player.hand[choice].getDebtPrice(player)
		player.trash(choice)
		options = []
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and player.session.piles[pile].viewTop().getPrice(player)<=coinVal+2 and player.session.piles[pile].viewTop().getPotionPrice(player)<=potionVal and player.session.piles[pile].viewTop().getDebtPrice(player)<=debtPrice: options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.session.piles[options[choice]])
		
class Smithy(Action, CardAdd):
	name = 'Smithy'
	def __init__(self, session, **kwargs):
		super(Smithy, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Smithy, self).onPlay(player, **kwargs)
		player.draw(amnt=3)
		
class Spy(Action, Attack, CardAdd):
	name = 'Spy'
	def __init__(self, session, **kwargs):
		super(Spy, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Spy, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
		for aplayer in player.session.getPlayers(player):
			aplayer.attack(self.attack, self, controller=player)
	def attack(self, player, **kwargs):
		if not player.revealPosition(-1, fromZ=player.library): return
		if kwargs['controller'].user(('Top', 'Discard'), ''):
			player.session.dp.send(signal='spyBottom')
			player.discardCard(player.library.pop())
		else:
			player.session.dp.send(signal='spyTop')

class Thief(Action, Attack, CardAdd):
	name = 'Thief'
	def __init__(self, session, **kwargs):
		super(Thief, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Thief, self).onPlay(player, **kwargs)
		for aplayer in player.session.getPlayers(player):
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
				if gain: kwargs['controller'].gain(card, player.session.trash)
			else: player.discardCard(card)
			
class ThroneRoom(Action, CardAdd):
	name = 'Throne Room'
	def __init__(self, session, **kwargs):
		super(ThroneRoom, self).__init__(session, **kwargs)
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
		player.session.dp.connect(self.trigger, signal='destroy')
		for i in range(2): player.playAction(options[choice])
	def onDestroy(self, player, **kwargs):
		if self.links: return True
	def onLeavePlay(self, player, **kwargs):
		if self.links: player.session.dp.disconnect(self.trigger, signal='destroy')
	def trigger(self, signal, **kwargs):
		print('THRONE ROOM DESTROY TRIGGER', self, kwargs['card'], self.links)
		if kwargs['card']==self: return
		for i in range(len(self.links)-1, -1, -1):
			if self.links[i]==kwargs['card']: self.links.pop(i)
		print('LINKS', self.links)
		if self.links: return
		print('NO LINKS')
		self.owner.destroy(self)
		
class CouncilRoom(Action, CardAdd):
	name = 'Council Room'
	def __init__(self, session, **kwargs):
		super(CouncilRoom, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(CouncilRoom, self).onPlay(player, **kwargs)
		player.draw(amnt=3)
		player.addBuy()
		for aplayer in player.session.getPlayers(player):
			aplayer.draw()
			
class Festival(Action, CardAdd):
	name = 'Festival'
	def __init__(self, session, **kwargs):
		super(Festival, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Festival, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		player.addAction(amnt=2)
		player.addBuy()
		
class Laboratory(Action, CardAdd):
	name = 'Laboratory'
	def __init__(self, session, **kwargs):
		super(Laboratory, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Laboratory, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		player.addAction()
		
class Library(Action, CardAdd):
	name = 'Library'
	def __init__(self, session, **kwargs):
		super(Library, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Library, self).onPlay(player, **kwargs)
		aside = []
		while len(player.hand)<8 and player.draw():
			if 'ACTION' in player.hand[-1].types and not player.user((player.hand[-1].name, 'NotSetAside'), ''):
				actionCard = player.hand.pop()
				player.reveal(actionCard)
				aside.append(actionCard)
		while aside: player.discard(aside.pop())
			
class Market(Action, CardAdd):
	name = 'Market'
	def __init__(self, session, **kwargs):
		super(Market, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Market, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		player.addCoin()
		player.addBuy()
		
class Mine(Action, CardAdd):
	name = 'Mine'
	def __init__(self, session, **kwargs):
		super(Mine, self).__init__(session, **kwargs)
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
				coinVal, potionVal, debtPrice = player.hand[i].getPrice(player), player.hand[i].getPotionPrice(player), player.hand[choice].getDebtPrice(player)
				player.trash(i)
				break
		options = []
		for pile in player.session.piles:
			if 'TREASURE' in player.session.piles[pile].viewTop().types and player.session.piles[pile].viewTop().getPrice(player)<=coinVal+3 and player.session.piles[pile].viewTop().getPotionPrice(player)<=potionVal and player.session.piles[pile].viewTop().getDebtPrice(player)<=debtPrice:
				options.append(player.session.piles[pile])
		if not options: return
		choice = player.user([o.name for o in options], 'Choose gain')
		player.gainFromPile(options[choice], to=player.hand)
	
class Witch(Action, Attack, CardAdd):
	name = 'Witch'
	def __init__(self, session, **kwargs):
		super(Witch, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Witch, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		for aplayer in player.session.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self, controller=player)
	def attack(self, player, **kwargs):
		player.gainFromPile(player.session.piles['Curse'])
		
class Adventurer(Action, CardAdd):
	name = 'Adventurer'
	def __init__(self, session, **kwargs):
		super(Adventurer, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Loan, self).__init__(session, **kwargs)
		self.value = 1
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Loan, self).onPlay(player, **kwargs)
		aside = []
		card = None
		treasure = None
		while True:
			card = player.getCard()
			if not card: break
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
	def __init__(self, session, **kwargs):
		super(TradeToken, self).__init__(session, **kwargs)
		session.dp.connect(self.onGain, signal='gain')
	def onGain(self, signal, **kwargs):
		if 'fromz' in kwargs and kwargs['fromz']==self.owner:
			for i in range(len(self.owner.tokens)):
				if self.owner.tokens[i]==self:
					self.session.globalMats['TradeRouteMat'].append(self.owner.getToken(self, self.session))
					break
						
class TradeRoute(Action, CardAdd):
	name = 'Trade Route'
	def __init__(self, session, **kwargs):
		super(TradeRoute, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(TradeRoute, self).onPlay(player, **kwargs)
		player.addBuy()
		player.addCoin(amnt=len(player.session.globalMats['TradeRouteMat']))
		if player.hand: player.trash(player.user([o.name for o in player.hand], 'Choose trash'))
	def addTokens(self, **kwargs):
		for pile in kwargs['session'].piles:
			if kwargs['session'].piles[pile].viewTop() and 'VICTORY' in kwargs['session'].piles[pile].viewTop().types: kwargs['session'].piles[pile].addToken(TradeToken(kwargs['session']), kwargs['session'])
	def onPileCreate(self, pile, session, **kwargs):
		super(TradeRoute, self).onPileCreate(pile, session, **kwargs)
		session.delayedActions.append([self.addTokens, {'session': session}])
		session.addGlobalMat('TradeRouteMat')
			
class Watchtower(Action, Reaction, CardAdd):
	name = 'Watchtower'
	def __init__(self, session, **kwargs):
		super(Watchtower, self).__init__(session, **kwargs)
		Reaction.__init__(self, session, **kwargs)
		self.price = 3
		self.signal = 'gain'
	def onPlay(self, player, **kwargs):
		super(Watchtower, self).onPlay(player, **kwargs)
		while len(player.hand)<6 and player.draw(): pass
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and self in self.owner.hand and self.owner.user(('no', 'UseWatchTower'), ''):
			self.owner.reveal(self)
			if self.owner.user(('top', 'trash'), ''): 
				self.owner.trashCard(kwargs['card'])
				return True
			else: kwargs['kwargs']['to'] = self.owner.library
	def onGain(self, player, **kwargs):
		self.connect(session=player.session)
	def onTrash(self, player, **kwargs):
		self.disconnect(session=player.session)
	def onReturn(self, player, **kwargs):
		self.disconnect(session=player.session)
		
class Bishop(Action, CardAdd):
	name = 'Bishop'
	def __init__(self, session, **kwargs):
		super(Bishop, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Bishop, self).onPlay(player, **kwargs)		
		player.addCoin()
		player.addVictory()
		if player.hand:
			choice = player.user([o.name for o in player.hand], 'Choose trash')
			player.addVictory(amnt=m.floor(player.hand[choice].getPrice(player)/2))
			player.trash(choice)
		for aplayer in player.session.getPlayers(player):
			if aplayer==player: continue
			choice = aplayer.user([o.name for o in aplayer.hand]+['NoTrash'], 'Choose trash')
			if choice+1>len(aplayer.hand): continue
			aplayer.trash(choice)
			
class Monument(Action, CardAdd):
	name = 'Monument'
	def __init__(self, session, **kwargs):
		super(Monument, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Monument, self).onPlay(player, **kwargs)
		player.addVictory()
		player.addCoin(amnt=2)
		
class Quarry(Treasure, CardAdd):
	name = 'Quarry'
	def __init__(self, session, **kwargs):
		super(Quarry, self).__init__(session, **kwargs)
		self.price = 4
		self.value = 1
	def onPlay(self, player, **kwargs):
		super(Quarry, self).onPlay(player, **kwargs)
		for card in player.session.allCards:
			if 'ACTION' in card.types: card.price-=2
	def onLeavePlay(self, player, **kwargs):
		for card in player.session.allCards:
			if 'ACTION' in card.types: card.price+=2
			
class Talisman(Treasure, CardAdd):
	name = 'Talisman'
	def __init__(self, session, **kwargs):
		super(Talisman, self).__init__(session, **kwargs)
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
		self.owner.session.dp.connect(self.trigger, signal='buy')
	def disconnect(self, **kwargs):
		self.owner.session.dp.disconnect(self.trigger, signal='buy')
	
class WorkersVillage(Action, CardAdd):
	name = "Worker's Village"
	def __init__(self, session, **kwargs):
		super(WorkersVillage, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(WorkersVillage, self).onPlay(player, **kwargs)	
		player.addAction(amnt=2)
		player.draw()
		player.addBuy()
		
class City(Action, CardAdd):
	name = 'City'
	def __init__(self, session, **kwargs):
		super(City, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(City, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		if len(player.session.emptyPiles)>0:
			player.draw(amnt=2)
			if len(player.session.emptyPiles)>1:
				player.addCoin()
				player.addBuy()
		else: player.draw()
		
class Contraband(Treasure, CardAdd):
	name = 'Contraband'
	def __init__(self, session, **kwargs):
		super(Contraband, self).__init__(session, **kwargs)
		self.price = 5
		self.value = 3
		self.banning = None
	def onPlay(self, player, **kwargs):
		super(Contraband, self).onPlay(player, **kwargs)
		player.addBuy()
		self.banning = player.session.piles[list(player.session.piles)[player.session.getNextPlayer(player).user(list(player.session.piles), 'Choose ban')]]
		player.session.dp.send(signal='Choice', choice=self.banning, card=self)
		self.connect()
	def onLeavePlay(self, player, **kwargs):
		self.disconnect()
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and kwargs['pile']==self.banning: return True
	def connect(self, **kwargs):
		self.owner.session.dp.connect(self.trigger, signal='tryBuy')
	def disconnect(self, **kwargs):
		self.owner.session.dp.disconnect(self.trigger, signal='tryBuy')	
		
class CountingHouse(Action, CardAdd):
	name = 'Counting House'
	def __init__(self, session, **kwargs):
		super(CountingHouse, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(CountingHouse, self).onPlay(player, **kwargs)
		coppers = 0
		for card in player.discardPile:
			if card.name=='Copper': coppers+=1
		for i in range(player.user(list(range(coppers+1)), 'Choose amnount')):
			for n in range(len(player.discardPile)-1, -1, -1):
				if player.discardPile[n].name=='Copper':
					player.reveal(player.discardPile[n])
					player.hand.append(player.discardPile.pop(n))
					break
		
class Mint(Action, CardAdd):
	name = 'Mint'
	def __init__(self, session, **kwargs):
		super(Mint, self).__init__(session, **kwargs)
		self.price = 5
		session.dp.connect(self.trigger, signal='buy')
	def onPlay(self, player, **kwargs):
		super(Mint, self).onPlay(player, **kwargs)
		options = []
		for card in player.hand:
			if 'TREASURE' in card.types: options.append(card.name)
		if not options: return
		choice = player.user(options+['NoMint'], 'Choose gain')
		if choice>=len(options): return
		player.gainFromPile(player.session.piles[options[choice]])
	def trigger(self, signal, **kwargs):
		if 'pile' in kwargs and not self==kwargs['pile'].viewTop(): return
		for i in range(len(kwargs['player'].inPlay)-1, -1, -1):
			if 'TREASURE' in kwargs['player'].inPlay[i].types: kwargs['player'].trashCard(kwargs['player'].getFromPlay(i))
		
class Mountebank(Action, Attack, CardAdd):
	name = 'Mountebank'
	def __init__(self, session, **kwargs):
		super(Mountebank, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Mountebank, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for aplayer in player.session.getPlayers(player):
			if not player==aplayer: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		for i in range(len(player.hand)):
			if player.hand[i].name=='Curse':
				if player.user(('keep', 'discardCurse'), ''):
					player.discard(i)
					return
				break
		player.gainFromPile(player.session.piles['Curse'])
		player.gainFromPile(player.session.piles['Copper'])

class Rabble(Action, Attack, CardAdd):
	name = 'Rabble'
	def __init__(self, session, **kwargs):
		super(Rabble, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Rabble, self).onPlay(player, **kwargs)
		player.draw(amnt=3)
		for aplayer in player.session.getPlayers(player):
			if not player==aplayer: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		cards = player.getCards(3)
		for i in range(len(cards)-1, -1, -1):
			if 'ACTION' in cards[i].types or 'TREASURE' in cards[i].types: player.discardCard(cards.pop(i))
		while cards:
			player.library.append(cards.pop(player.user([o.name for o in cards], 'Choose top')))

class Vault(Action, CardAdd):
	name = 'Vault'
	def __init__(self, session, **kwargs):
		super(Vault, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Vault, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		while player.hand:
			choice = player.user([o.name for o in player.hand]+['EndDiscard'], 'Choose discard')
			if choice>len(player.hand): break
			player.discard(choice)
			player.addCoin()
		for aplayer in player.session.getPlayers(player):
			if len(aplayer.hand)>1 and aplayer.user(('discard', 'DoNotDiscard'), ''):
				for i in range(2): aplayer.discard(aplayer.user([o.name for o in aplayer.hand], 'Choose discard '+str(1+i)))
				aplayer.draw()

class Venture(Treasure, CardAdd):
	name = 'Venture'
	def __init__(self, session, **kwargs):
		super(Venture, self).__init__(session, **kwargs)
		self.price = 5
		self.value = 1
	def onPlay(self, player, **kwargs):
		super(Venture, self).onPlay(player, **kwargs)
		aside = []
		card = None
		treasure = None
		while True:
			card = player.getCard()
			if not card: break
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
	def __init__(self, session, **kwargs):
		super(Goons, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 6
	def onPlay(self, player, **kwargs):
		super(Goons, self).onPlay(player, **kwargs)
		self.connect()
		player.addBuy()
		player.addCoin(amnt=2)
		for aplayer in player.session.getPlayers(player):
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
		player.session.dp.connect(self.trigger, signal='buy')
	def disconnect(self, **kwargs):
		player.session.dp.disconnect(self.trigger, signal='buy')
		
class GrandMarket(Action, CardAdd):
	name = 'Grand Market'
	def __init__(self, session, **kwargs):
		super(GrandMarket, self).__init__(session, **kwargs)
		self.price = 6
		session.dp.connect(self.trigger, signal='tryBuy')
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
	def __init__(self, session, **kwargs):
		super(Hoard, self).__init__(session, **kwargs)
		self.price = 6
		self.value = 2
	def onPlay(self, player, **kwargs):
		super(Hoard, self).onPlay(player, **kwargs)
		self.connect()
	def onLeavePlay(self, player, **kwargs):
		self.disconnect()
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and 'pile' in kwargs and kwargs['pile'].viewTop() and 'VICTORY' in kwargs['pile'].viewTop().types:
			self.owner.gainFromPile(self.owner.session.piles['Gold'])
	def connect(self, **kwargs):
		self.owner.session.dp.connect(self.trigger, signal='buy')
	def disconnect(self, **kwargs):
		self.owner.session.dp.disconnect(self.trigger, signal='buy')

class Bank(Treasure, CardAdd):
	name = 'Bank'
	def __init__(self, session, **kwargs):
		super(Bank, self).__init__(session, **kwargs)
		self.price = 7
	def onPlay(self, player, **kwargs):
		vsum = 0
		for card in player.inPlay:
			if 'TREASURE' in card.types: vsum+=1
		player.addCoin(amnt=vsum)
		
class Expand(Action, CardAdd):
	name = 'Expand'
	def __init__(self, session, **kwargs):
		super(Expand, self).__init__(session, **kwargs)
		self.price = 7
	def onPlay(self, player, **kwargs):
		super(Expand, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		coinVal, potionVal, debtPrice = player.hand[choice].getPrice(player), player.hand[choice].getPotionPrice(player), player.hand[choice].getDebtPrice(player)
		player.trash(choice)
		options = []
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and player.session.piles[pile].viewTop().getPrice(player)<=coinVal+3 and player.session.piles[pile].viewTop().getPotionPrice(player)<=potionVal and player.session.piles[pile].viewTop().getDebtPrice(player)<=debtPrice:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.session.piles[options[choice]])
		
class Forge(Action, CardAdd):
	name = 'Forge'
	def __init__(self, session, **kwargs):
		super(Forge, self).__init__(session, **kwargs)
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
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and player.session.piles[pile].viewTop().getPrice(player)==trashedValue:
				options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.session.piles[options[choice]])
		
class KingsCourt(Action, CardAdd):
	name = "King's Court"
	def __init__(self, session, **kwargs):
		super(KingsCourt, self).__init__(session, **kwargs)
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
		choice = player.user([o.name for o in options], 'Choose action')
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]:
				player.inPlay.append(player.hand.pop(i))
				break
		self.links.append(options[choice])
		player.session.dp.connect(self.trigger, signal='destroy')
		for i in range(3): player.playAction(options[choice])
	def onDestroy(self, player, **kwargs):
		if self.links: return True
	def onLeavePlay(self, player, **kwargs):
		if self.links: player.session.dp.disconnect(self.trigger, signal='destroy')
	def trigger(self, signal, **kwargs):
		if kwargs['card']==self: return
		for i in range(len(self.links)-1, -1, -1):
			if self.links[i]==kwargs['card']: self.links.pop(i)
		if self.links: return
		self.owner.destroy(self)

class Peddler(Action, CardAdd):
	name = 'Peddler'
	def __init__(self, session, **kwargs):
		super(Peddler, self).__init__(session, **kwargs)
		self.price = 8
	def onPlay(self, player, **kwargs):
		super(Peddler, self).onPlay(player, **kwargs)
		player.addCoin()
		player.addAction()
		player.draw()
	def getPrice(self, player, **kwargs):
		isBuy = False
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='actionPhase' or player.session.events[i][0]=='treasurePhase': break
			elif player.session.events[i][0]=='buyPhase':
				isBuy = player.session.events[i][1]['player']==player
				break
		if not isBuy: return np.max((self.price, 0))
		actions = 0
		for card in player.inPlay:
			if 'ACTION' in card.types: actions+=1
		return np.max((self.price-actions*2, 0))
		
prosperity = [Loan, TradeRoute, Watchtower, Bishop, Monument, Quarry, Talisman, WorkersVillage, City, Contraband, CountingHouse, Mint, Mountebank, Rabble, Vault, Venture, Goons, GrandMarket, Hoard, Bank, Expand, Forge, KingsCourt, Peddler]

class Colony(Victory, CardAdd):
	name = 'Colony'
	def __init__(self, session, **kwargs):
		super(Colony, self).__init__(session, **kwargs)
		self.value = 10
		self.price = 11
	def onPileCreate(self, pile, session, **kwargs):
		pile.terminator = True
		if len(session.players)>3:
			amnt = 12
		else:
			amnt = 8
		for i in range(amnt):
			pile.append(type(self)(session))
			
class Platinum(Treasure, CardAdd):
	name = 'Platinum'
	def __init__(self, session, **kwargs):
		super(Platinum, self).__init__(session, **kwargs)
		self.value = 5
		self.price = 9
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(12):
			pile.append(type(self)(session))
			
platColony = [Colony, Platinum]

class EmbargoToken(Token):
	name = 'Embargo Token'
	def __init__(self, session, **kwargs):
		super(EmbargoToken, self).__init__(session, **kwargs)
		session.dp.connect(self.trigger, signal='buy')
	def trigger(self, signal, **kwargs):
		if kwargs['pile']==self.owner:
			print('EMBARGO', kwargs['player'])
			kwargs['player'].gainFromPile(player.session.piles['Curse'])
						
class Embargo(Action, CardAdd):
	name = 'Embargo'
	def __init__(self, session, **kwargs):
		super(Embargo, self).__init__(session, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Embargo, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.trashCard(player.getFromPlay(i))
				break
		player.session.piles[list(player.session.piles)[player.user(list(player.session.piles), 'Choose embargo')]].addToken(EmbargoToken(player.session), player.session)
	
class Haven(Action, Duration, CardAdd):
	name = 'Haven'
	def __init__(self, session, **kwargs):
		super(Haven, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 2
		self.saved = []
	def onPlay(self, player, **kwargs):
		super(Haven, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		self.age = 0
		player.session.dp.connect(self.nextage, signal='startTurn')
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
	def __init__(self, session, **kwargs):
		super(Lighthouse, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		player.addAction()
		player.addCoin()
		self.age = 0
		self.nexts.append(self.next)
		player.session.dp.connect(self.nextage)
	def nextage(self, signal, **kwargs):
		if signal=='startTurn' and kwargs['player']==self.owner:
			self.age+=1
			while self.nexts:
				self.owner.session.dp.send(signal='duration', card=self)
				self.nexts.pop()()
		elif signal=='attack' and kwargs['player']==self.owner: return True
	def next(self, **kwargs):
		self.owner.addCoin()
		
class NativeVillage(Action, CardAdd):
	name = 'Native Village'
	def __init__(self, session, **kwargs):
		super(NativeVillage, self).__init__(session, **kwargs)
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
	def onPileCreate(self, pile, session, **kwargs):
		super(NativeVillage, self).onPileCreate(pile, session, **kwargs)
		session.addMat('NativeVillageMat')

class PearlDiver(Action, CardAdd):
	name = 'Pearl Diver'
	def __init__(self, session, **kwargs):
		super(PearlDiver, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Ambassador, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Ambassador, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose return')
		revealedCard = player.hand[choice]
		player.reveal(revealedCard)
		if not revealedCard.name in player.session.piles: return
		amnt = player.user(list(range(3)), 'Choose return amount')
		returned = 0
		for i in range(len(player.hand)-1, -1, -1):
			if returned==amnt: break
			if player.hand[i].name==revealedCard.name:
				player.returnCard(player.hand.pop(i))
				returned+=1
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self, pile=player.session.piles[revealedCard.name])
	def attack(self, player, **kwargs):
		player.gainFromPile(kwargs['pile'])
		
class FishingVillage(Action, Duration, CardAdd):
	name = 'Fishing Village'
	def __init__(self, session, **kwargs):
		super(FishingVillage, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Lookout, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Smugglers, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Smugglers, self).onPlay(player, **kwargs)
		previousPlayer = player.session.getPreviousPlayer(player)
		options = []
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='startTurn' and player.session.events[i][1]['player']==previousPlayer:
				for n in range(i, len(player.session.events)):
					if player.session.events[n][0]=='gain' and player.session.events[n][1]['player']==previousPlayer and player.session.events[n][1]['card'].getPrice(player)<7: options.append(player.session.events[n][1]['card'].name)
					elif player.session.events[n][0]=='endTurn': break
				break
		if not options: return
		player.gainFromPile(player.session.piles[options[player.user(options, 'Choose smuggle')]])
					
class Warehouse(Action, CardAdd):
	name = 'Warehouse'
	def __init__(self, session, **kwargs):
		super(Warehouse, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Caravan, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Caravan, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
	def next(self, **kwargs):
		self.owner.draw()
		
class Cutpurse(Action, CardAdd):
	name = 'Cutpurse'
	def __init__(self, session, **kwargs):
		super(Cutpurse, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Cutpurse, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for aplayer in player.session.getPlayers(player):
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
	def __init__(self, session, **kwargs):
		super(Island, self).__init__(session, **kwargs)
		Victory.__init__(self, session, **kwargs)
		self.price = 4
		self.value = 2
	def onPlay(self, player, **kwargs):
		super(Island, self).onPlay(player, **kwargs)
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self: player.mats['IslandMat'].append(player.getFromPlay(i))
		if not player.hand: return
		player.mats['IslandMat'].append(player.hand.pop(player.user([o.name for o in player.hand], 'Choose hide')))
	def onPileCreate(self, pile, session, **kwargs):
		super(Island, self).onPileCreate(pile, session, **kwargs)
		session.addMat('IslandMat')
		
class Navigator(Action, CardAdd):
	name = 'Navigator'
	def __init__(self, session, **kwargs):
		super(Navigator, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(PirateShip, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(PirateShip, self).onPlay(player, **kwargs)
		if player.user(('attack', 'money'), ''): player.addCoin(amnt=len(player.mats['PirateMat']))
		else:
			for aplayer in player.session.getPlayers(player):
				if not player==aplayer: aplayer.attack(self.attack, self)
	def onPileCreate(self, pile, session, **kwargs):
		super(PirateShip, self).onPileCreate(pile, session, **kwargs)
		session.addMat('PirateMat')
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
					self.owner.mats['PirateMat'].append(PirateToken(player.session))
					break
		while cards: player.discardCard(cards.pop())
		
class Salvager(Action, CardAdd):
	name = 'Salvager'
	def __init__(self, session, **kwargs):
		super(Salvager, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(SeaHag, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(SeaHag, self).onPlay(player, **kwargs)
		for aplayer in player.session.getPlayers(player):
			if not player==aplayer: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		player.discardCard(player.getCard())
		player.gainFromPile(player.session.piles['Curse'], to=player.library)
		
class TreasureMap(Action, CardAdd):
	name = 'Treasure Map'
	def __init__(self, session, **kwargs):
		super(TreasureMap, self).__init__(session, **kwargs)
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
				for n in range(4): player.gainFromPile(player.session.piles['Gold'], to=player.library)
				return
		
class Bazaar(Action, CardAdd):
	name = 'Bazaar'
	def __init__(self, session, **kwargs):
		super(Bazaar, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Bazaar, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		player.draw()
		player.addCoin()
		
class Explorer(Action, CardAdd):
	name = 'Explorer'
	def __init__(self, session, **kwargs):
		super(Explorer, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Explorer, self).onPlay(player, **kwargs)
		if player.hand and player.user(('no', 'revealProvince'), ''):
			for card in player.hand:
				if card.name=='Province':
					player.gainFromPile(player.session.piles['Gold'], to=player.hand)
					return
		player.gainFromPile(player.session.piles['Silver'], to=player.hand)
		
class GhostShip(Action, Attack, CardAdd):
	name = 'Ghost Ship'
	def __init__(self, session, **kwargs):
		super(GhostShip, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(GhostShip, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		for aplayer in player.session.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		while len(player.hand)>3:
			choice = player.user([o.name for o in player.hand], 'Choose top')
			player.library.append(player.hand.pop(choice))
		
class MerchantShip(Action, Duration, CardAdd):
	name = 'Merchant Ship'
	def __init__(self, session, **kwargs):
		super(MerchantShip, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(MerchantShip, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
	def next(self, **kwargs):
		self.owner.addCoin(amnt=2)
		
class Tactician(Action, Duration, CardAdd):
	name = 'Tactician'
	def __init__(self, session, **kwargs):
		super(Tactician, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Tactician, self).onPlay(player, **kwargs)
		player.session.dp.connect(self.trigger, signal='startTurn')
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
	def __init__(self, session, **kwargs):
		super(Treasury, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Treasury, self).onPlay(player, **kwargs)
		player.addAction()
		player.addCoin()
		player.draw()
	def onDestroy(self, player, **kwargs):
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='buy' and player.session.events[i][1]['card'] and 'VICTORY' in player.session.events[i][1]['card'].types: return
			elif player.session.events[i][0]=='startTurn': break
		if not player.user(('discard', 'top'), 'Treasury'): return
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.library.append(player.inPlay.pop(i))
				return True

class Outpost(Action, Duration, CardAdd):
	name = 'Outpost'
	def __init__(self, session, **kwargs):
		super(Outpost, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Outpost, self).onPlay(player, **kwargs)
		player.eotdraw = 3
		player.session.delayedActions.append((self.outpostTurn, {'player': player}))
	def outpostTurn(self, **kwargs):
		turns = 0
		for i in range(len(self.owner.session.events)-1, -1, -1):
			if self.owner.session.events[0]=='startTurn':
				if self.owner.session.event[1]['player']==self: turns+=1
				else: break
		if turns>1: return
		self.owner.session.activePlayer = self.owner
		self.owner.session.turnFlag = 'outpost'
		kwargs['player'].resetValues()
		self.owner.session.dp.send(signal='startTurn', player=self.owner, flags=self.owner.session.turnFlag)
		kwargs['player'].actionPhase()
		kwargs['player'].treasurePhase()
		kwargs['player'].buyPhase()
		kwargs['player'].endTurn()
			
seaside = [Embargo, Haven, Lighthouse, NativeVillage, Ambassador, FishingVillage, Lookout, Smugglers, Caravan, Cutpurse, Island, Navigator, PirateShip, Salvager, SeaHag, TreasureMap, Bazaar, Explorer, GhostShip, MerchantShip, Outpost, Tactician, Treasury]

class BoonToken(Token):
	name = 'Base Boon Token'
	def __init__(self, session, **kwargs):
		super(BoonToken, self).__init__(session, **kwargs)
		self.types.append('BOONTOKEN')
	def trigger(self, signal, **kwargs):
		if kwargs['card'].name==self.owner.cardType.name and kwargs['player']==self.playerOwner: self.boon(self.playerOwner)
	def boon(self, player, **kwargs):
		pass
	def onAddPile(self, pile, **kwargs):
		pile.session.dp.connect(self.trigger, signal='playAction')
	def onLeavePile(self, pile, **kwargs):
		pile.session.dp.disconnect(self.trigger, signal='playAction')

class PlusCard(BoonToken):
	name = 'Plus Card Token'
	def boon(self, player, **kwargs):
		player.draw()
		
class PlusAction(BoonToken):
	name = 'Plus Action Token'
	def boon(self, player, **kwargs):
		player.addAction()
		
class PlusBuy(BoonToken):
	name = 'Plus Buy Token'
	def boon(self, player, **kwargs):
		player.addBuy()
		
class PlusCoin(BoonToken):
	name = 'Plus Coin Token'
	def boon(self, player, **kwargs):
		player.addCoin()
		
class CoinOfTheRealm(Treasure, Reserve, CardAdd):
	name = 'Coin of the Realm'
	def __init__(self, session, **kwargs):
		super(CoinOfTheRealm, self).__init__(session, **kwargs)
		Reserve.__init__(self, session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Page, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = TreasureHunter 
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Page, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.draw()
		player.addAction()
		
class TreasureHunter(Action, Traveler, CardAdd):
	name = 'Treasure Hunter'
	def __init__(self, session, **kwargs):
		super(TreasureHunter, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Warrior 
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(TreasureHunter, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.addCoin()
		player.addAction()
		previousPlayer = None
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='startTurn' and player.session.events[i][1]['player']!=player:
				previousPlayer = player.session.events[i][1]['player']
				for n in range(i, len(player.session.events)):
					if player.session.events[n][0]=='gain' and player.session.events[n][1]['player']==previousPlayer: player.gainFromPile(player.session.piles['Silver'])
					elif player.session.events[n][0]=='endTurn': return
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.append(type(self)(session))
				
class Warrior(Action, Traveler, Attack, CardAdd):
	name = 'Warrior'
	def __init__(self, session, **kwargs):
		super(Warrior, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.morph = Hero 
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Warrior, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.draw(amnt=2)
		travelers = 0
		for card in player.inPlay:
			if 'TRAVELER' in card.types: travelers += 1
		for aplayer in player.session.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self, amnt=travelers)
	def attack(self, player, **kwargs):
		for i in range(kwargs['amnt']):
			card = player.getCard()
			if not card: break
			player.discardCard(card)
			if not (card.getPrice(player) in (3, 4) and card.getPotionPrice(player)==0) and card.getDebtPrice(player)==0: continue
			for i in range(len(player.discardPile)-1, -1, -1):
				if player.discardPile[i]==card: player.trashCard(player.discardPile.pop(i))
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.append(type(self)(session))
				
class Hero(Action, Traveler, CardAdd):
	name = 'Hero'
	def __init__(self, session, **kwargs):
		super(Hero, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Champion 
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Hero, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		options = []
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and 'TREASURE' in player.session.piles[pile].viewTop().types: options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.session.piles[options[choice]])
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.append(type(self)(session))
		
class Champion(Action, Duration, CardAdd):
	name = 'Champion'
	def __init__(self, session, **kwargs):
		super(Champion, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 6
	def onPlay(self, player, **kwargs):
		player.addAction()
		player.session.dp.connect(self.defence, signal='attack')
		player.session.dp.connect(self.addAction, signal='playAction')
	def defence(self, signal, **kwargs):
		if kwargs['player']==self.owner: return True
	def addAction(self, signal, **kwargs):
		if kwargs['player']==self.owner: self.owner.addAction()
	def onLeavePlay(self, player, **kwargs):
		pass
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(5): pile.append(type(self)(session))
		
class Peasant(Action, Traveler, CardAdd):
	name = 'Peasant'
	def __init__(self, session, **kwargs):
		super(Peasant, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Soldier 
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Peasant, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.addCoin()
		player.addBuy()

class Soldier(Action, Traveler, Attack, CardAdd):
	name = 'Soldier'
	def __init__(self, session, **kwargs):
		super(Soldier, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.morph = Fugitive 
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Soldier, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.addCoin(amnt=2)
		attacks = 0
		for card in player.inPlay:
			if 'ATTACK' in card.types and card!=self: attacks += 1
		player.addCoin(amnt=attacks)
		for aplayer in player.session.getPlayers(player):
			if aplayer==player: continue
			aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		if len(player.hand)>3: player.discard(player.user([o.name for o in player.hand], 'Choose discard'))
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.append(type(self)(session))
		
class Fugitive(Action, Traveler, CardAdd):
	name = 'Fugitive'
	def __init__(self, session, **kwargs):
		super(Fugitive, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
		self.morph = Disciple 
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Fugitive, self).onPlay(player, **kwargs)
		Traveler.onPlay(self, player, **kwargs)
		player.draw(amnt=2)
		player.addAction()
		if player.hand: player.discard(player.user([o.name for o in player.hand], 'Choose discard'))
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.append(type(self)(session))
		
class Disciple(Action, Traveler, CardAdd):
	name = 'Disciple'
	def __init__(self, session, **kwargs):
		super(Disciple, self).__init__(session, **kwargs)
		Traveler.__init__(self, session, **kwargs)
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
		choice = player.user([o.name for o in options]+['Play no action'], 'Choose action')
		if choice+1>len(options): return
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]:
				player.inPlay.append(player.hand.pop(i))
				break
		self.links.append(options[choice])
		player.session.dp.connect(self.trigger, signal='destroy')
		for i in range(2): player.playAction(options[choice])
		if options[choice].name in list(player.session.piles): player.gainFromPile(player.session.piles[options[choice].name])
	def onDestroy(self, player, **kwargs):
		super(Disciple, self).onDestroy(player, **kwargs)
		if self.links: return True
	def onLeavePlay(self, player, **kwargs):
		if self.links: player.session.dp.disconnect(self.trigger, signal='destroy')
	def trigger(self, signal, **kwargs):
		if kwargs['card']==self: return
		for i in range(len(self.links)-1, -1, -1):
			if self.links[i]==kwargs['card']: self.links.pop(i)
		if self.links: return
		self.owner.destroy(self)
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
		for i in range(5): pile.append(type(self)(session))

class Teacher(Action, Reserve, CardAdd):
	name = 'Teacher'
	def __init__(self, session, **kwargs):
		super(Teacher, self).__init__(session, **kwargs)
		Reserve.__init__(self, session, **kwargs)
		self.triggerSignal = 'startTurn'
		self.price = 6
	def call(self, signal, **kwargs):
		tokens = ('Plus Card Token', 'Plus Action Token', 'Plus Buy Token', 'Plus Coin Token')
		choice = self.owner.user(tokens, 'Choose token')
		token = self.owner.tokens[tokens[choice]]
		options = []
		for pile in self.owner.session.piles:
			hasBoon = False
			for pileToken in self.owner.session.piles[pile].tokens:
				if 'BOONTOKEN' in pileToken.types and pileToken.playerOwner==self.owner:
					hasBoon = True
					break
			if not hasBoon and 'ACTION' in self.owner.session.piles[pile].viewTop().types: options.append(pile)
		if not options: return
		pile = options[self.owner.user(options, 'Choose pile')]
		if token.owner:
			for i in range(len(token.owner.tokens)):
				if token==token.owner.tokens[i]:
					token.owner.getToken(token, self.owner.session)
					break
		self.owner.session.piles[pile].addToken(token, self.owner.session)
	def onPileCreate(self, pile, session, **kwargs):
		super(Teacher, self).onPileCreate(pile, session, **kwargs)
		session.addToken(PlusCard)
		session.addToken(PlusAction)
		session.addToken(PlusBuy)
		session.addToken(PlusCoin)
	
class Ratcatcher(Action, Reserve, CardAdd):
	name = 'Ratcatcher'
	def __init__(self, session, **kwargs):
		super(Ratcatcher, self).__init__(session, **kwargs)
		self.triggerSignal = 'startTurn'
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Ratcatcher, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
	def call(self, signal, **kwargs):
		if not self.owner.hand: return
		super(Ratcatcher, self).call(signal, **kwargs)
		self.owner.trash(self.owner.user([o.name for o in self.owner.hand], 'Choose trash'))
		
class Raze(Action, CardAdd):
	name = 'Raze'
	def __init__(self, session, **kwargs):
		super(Raze, self).__init__(session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Amulet, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
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
		elif choice==2: self.owner.gainFromPile(self.owner.session.piles['Silver'])
			
class CaravanGuard(Action, Duration, Reaction, CardAdd):
	name = 'Caravan Guard'
	def __init__(self, session, **kwargs):
		super(CaravanGuard, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		Reaction.__init__(self, session, **kwargs)
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
		kwargs['player'].session.dp.connect(self.trigger, signal=self.signal)
	def disconnect(self, **kwargs):
		kwargs['player'].session.dp.disconnect(self.trigger, signal=self.signal)
	def onGain(self, player, **kwargs):
		self.connect(player=player)
	def onTrash(self, player, **kwargs):
		self.disconnect(player=player)
	def onReturn(self, player, **kwargs):
		self.disconnect(player=player)

class Dungeon(Action, Duration, CardAdd):
	name = 'Dungeon'
	def __init__(self, session, **kwargs):
		super(Dungeon, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Gear, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 3
		self.saved = []
	def onPlay(self, player, **kwargs):
		super(Gear, self).onPlay(player, **kwargs)
		player.draw(amnt=2)
		self.age = 0
		player.session.dp.connect(self.next, signal='startTurn')
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
	def __init__(self, session, **kwargs):
		super(Guide, self).__init__(session, **kwargs)
		Reserve.__init__(self, session, **kwargs)
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
	def __init__(self, session, **kwargs):
		super(Duplicate, self).__init__(session, **kwargs)
		self.triggerSignal = 'gain'
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Duplicate, self).onPlay(player, **kwargs)
		Reserve.onPlay(self, player, **kwargs)
	def requirements(self, **kwargs):
		return self.owner==kwargs['player'] and kwargs['card'].getPrice(self.owner)<7 and kwargs['card'].name in list(self.owner.session.piles)
	def call(self, signal, **kwargs):
		super(Duplicate, self).call(signal, **kwargs)
		self.owner.gainFromPile(self.owner.session.piles[kwargs['card'].name])
			
class Magpie(Action, CardAdd):
	name = 'Magpie'
	def __init__(self, session, **kwargs):
		super(Magpie, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Magpie, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		revealedCard = player.revealPosition(-1, fromZ=player.library)
		if 'TREASURE' in revealedCard.types: player.draw()
		if 'ACTION' in revealedCard.types or 'VICTORY' in revealedCard.types: player.gainFromPile(player.session.piles['Magpie'])

class Messenger(Action, CardAdd):
	name = 'Messenger'
	def __init__(self, session, **kwargs):
		super(Messenger, self).__init__(session, **kwargs)
		self.price = 4
		session.dp.connect(self.trigger, signal='buy')
	def onPlay(self, player, **kwargs):
		super(Messenger, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		player.addBuy()
		if player.user(('no', 'yes'), 'Discard library'):
			player.session.dp.send(signal='Announce', message='Discard deck')
			while player.library:
				player.discardPile.append(player.library.pop())
	def trigger(self, signal, **kwargs):
		if not self==kwargs['card']: return
		for i in range(len(kwargs['player'].session.events)-1, -1, -1):
			if kwargs['player'].session.events[i][0]=='buy' and kwargs['player'].session.events[i][1]['card']!=self: return
			elif kwargs['player'].session.events[i][0]=='startTurn': break
		options = []
		for pile in kwargs['player'].session.piles:
			if kwargs['player'].session.piles[pile].viewTop() and kwargs['player'].session.piles[pile].viewTop().getPrice(kwargs['player'])<5 and kwargs['player'].session.piles[pile].viewTop().getPotionPrice(kwargs['player'])<1 and player.session.piles[pile].viewTop().getDebtPrice(kwargs['player'])<1: options.append(pile)
		if not options: return
		choice = kwargs['player'].user(options, 'Choose gain')
		for player in kwargs['player'].session.getPlayers(kwargs['player']): player.gainFromPile(kwargs['player'].session.piles[options[choice]])

class Miser(Action, CardAdd):
	name = 'Miser'
	def __init__(self, session, **kwargs):
		super(Miser, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Miser, self).onPlay(player, **kwargs)
		if player.user(('Coins', 'Hide Copper'), 'Choose mode'):
			for i in range(len(player.hand)):
				if player.hand[i].name=='Copper':
					player.mats['Tavern'].append(player.hand.pop(i))
					break
		else:
			coppers = 0
			for card in player.mats['Tavern']:
				if card.name=='Copper': coppers += 1
			player.addCoin(amnt=coppers)
	def onPileCreate(self, pile, session, **kwargs):
		super(Miser, self).onPileCreate(pile, session, **kwargs)
		session.addMat('Tavern')
	
class Port(Action, CardAdd):
	name = 'Port'
	def __init__(self, session, **kwargs):
		super(Port, self).__init__(session, **kwargs)
		self.price = 4
		session.dp.connect(self.trigger, signal='buy')
	def onPlay(self, player, **kwargs):
		super(Port, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		player.draw()
	def trigger(self, signal, **kwargs):
		if 'pile' in kwargs and not self==kwargs['pile'].viewTop(): return
		kwargs['player'].gainFromPile(kwargs['player'].session.piles['Port'])
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(12):
			pile.append(type(self)(session))

class Ranger(Action, CardAdd):
	name = 'Ranger'
	def __init__(self, session, **kwargs):
		super(Ranger, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Ranger, self).onPlay(player, **kwargs)
		player.addBuy()
		if player.flipJourney(): player.draw(amnt=5)

class Transmogrify(Action, Reserve, CardAdd):
	name = 'Transmogrify'
	def __init__(self, session, **kwargs):
		super(Transmogrify, self).__init__(session, **kwargs)
		self.triggerSignal = 'startTurn'
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Transmogrify, self).onPlay(player, **kwargs)
		player.addAction()
	def call(self, signal, **kwargs):
		if not self.owner.hand: return
		super(Transmogrify, self).call(signal, **kwargs)
		choice = self.owner.user([o.name for o in self.owner.hand], 'Choose trash')
		trashedCard = self.owner.hand[choice]
		coinVal, potionVal, debtPrice = trashedCard.getPrice(self.owner), trashedCard.getPotionPrice(self.owner), trashedCard.getDebtPrice(self.owner)
		self.owner.trash(choice)
		options = []
		for pile in self.owner.session.piles:
			if self.owner.session.piles[pile].viewTop() and self.owner.session.piles[pile].viewTop().getPrice(self.owner)==coinVal+1 and self.owner.session.piles[pile].viewTop().getPotionPrice(self.owner)==potionVal and player.session.piles[pile].viewTop().getDebtPrice(player)==debtPrice:
				options.append(pile)
		if not options: return
		choice = self.owner.user(options, 'Choose gain')
		self.owner.gainFromPile(self.owner.session.piles[options[choice]], to=self.owner.hand)

class Artificer(Action, CardAdd):
	name = 'Artificer'
	def __init__(self, session, **kwargs):
		super(Artificer, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Artificer, self).onPlay(player, **kwargs)
		player.addCoin()
		player.addAction()
		player.draw()
		discarded = 0
		while player.hand:
			choice = player.user([o.name for o in player.hand]+['endDiscard'], 'Choose discard '+str(discarded+1))
			if choice+1>len(player.hand): break
			player.discard(choice)
			discarded += 1
		options = []
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and player.session.piles[pile].viewTop().getPrice(player)==discarded and player.session.piles[pile].viewTop().getPotionPrice(player)==0 and player.session.piles[pile].viewTop().getDebtPrice(player)==0:
				options.append(pile)
		if not options: return
		choice = player.user(options + ['No gain'], 'Choose gain')
		if choice+1>len(options): return
		player.gainFromPile(player.session.piles[options[choice]])

class BridgeTroll(Action, Duration, Attack, CardAdd):
	name = 'Bridge Troll'
	def __init__(self, session, **kwargs):
		super(BridgeTroll, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 5
		self.reduction = 0
	def onPlay(self, player, **kwargs):
		super(BridgeTroll, self).onPlay(player, **kwargs)
		player.addBuy()
		self.reduce()
		self.connect()
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self)
	def startTrigger(self, signal, **kwargs):
		if kwargs['player']==self.owner: self.reduce()
	def endTrigger(self, signal, **kwargs):
		if kwargs['player']==self.owner: self.inflate()
	def connect(self):
		self.owner.session.dp.connect(self.startTrigger, signal='startTurn')
		self.owner.session.dp.connect(self.endTrigger, signal='endTurn')
	def disconnect(self):
		self.owner.session.dp.disconnect(self.startTrigger, signal='startTurn')
		self.owner.session.dp.disconnect(self.endTrigger, signal='endTurn')
	def onLeavePlay(self, player, **kwargs):
		self.inflate()
		self.disconnect()
	def next(self, **kwargs):
		self.owner.addBuy()
	def attack(self, player, **kwargs):
		player.minusCoin = True
	def reduce(self):
		if self.reduction>0: return
		self.reduction += 1
		for card in self.owner.session.allCards: card.price -= 1
	def inflate(self):
		for card in self.owner.session.allCards: card.price += self.reduction
		self.reduction = 0

class DistantLands(Action, Victory, CardAdd):
	name = 'Distant Lands'
	def __init__(self, session, **kwargs):
		super(DistantLands, self).__init__(session, **kwargs)
		Victory.__init__(self, session, **kwargs)
		self.price = 5
		self.value = 0
	def onPlay(self, player, **kwargs):
		super(DistantLands, self).onPlay(player, **kwargs)
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.mats['Tavern'].append(player.inPlay.pop(i))
				self.value = 4
				break
	def onPileCreate(self, pile, session, **kwargs):
		super(DistantLands, self).onPileCreate(pile, session, **kwargs)
		session.addMat('Tavern')
		
class Giant(Action, Attack, CardAdd):
	name = 'Giant'
	def __init__(self, session, **kwargs):
		super(Giant, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Giant, self).onPlay(player, **kwargs)
		if player.flipJourney():
			player.addCoin(amnt=5)
			for aplayer in player.session.getPlayers(player):
				if not aplayer==player: aplayer.attack(self.attack, self)
		else: player.addCoin()
	def attack(self, player, **kwargs):
		card = player.getCard()
		if card and card.getPrice(player)>2 and card.getPrice(player)<7: player.trashCard(card)
		elif card:
			player.discardCard(card)
			player.gainFromPile(player.session.piles['Curse'])
		else: player.gainFromPile(player.session.piles['Curse'])
		
class HauntedWoods(Action, Attack, Duration, CardAdd):
	name = 'Haunted Woods'
	def __init__(self, session, **kwargs):
		super(HauntedWoods, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 5
		self.attacking = []
	def onPlay(self, player, **kwargs):
		super(HauntedWoods, self).onPlay(player, **kwargs)
		self.attacking = []
		player.session.dp.connect(self.trigger, signal='buy')
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self)
	def onLeavePlay(self, player, **kwargs):
		player.session.dp.disconnect(self.trigger, signal='buy')
	def trigger(self, signal, **kwargs):
		if not kwargs['player'] in self.attacking: return
		while kwargs['player'].hand: kwargs['player'].library.append(kwargs['player'].hand.pop())
	def attack(self, player, **kwargs):
		kwargs['card'].attacking.append(player)
	def next(self, **kwargs):
		self.owner.draw(amnt=3)

class LostCity(Action, CardAdd):
	name = 'Lost City'
	def __init__(self, session, **kwargs):
		super(LostCity, self).__init__(session, **kwargs)
		self.price = 5
		session.dp.connect(self.trigger, signal='buy')
	def onPlay(self, player, **kwargs):
		super(LostCity, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		player.draw(amnt=2)
	def trigger(self, signal, **kwargs):
		if 'pile' in kwargs and not self==kwargs['pile'].viewTop(): return
		for aplayer in kwargs['player'].session.getPlayers(kwargs['player']):
			if not aplayer==kwargs['player']: aplayer.draw()

class Relic(Treasure, Attack, CardAdd):
	name = 'Relic'
	def __init__(self, session, **kwargs):
		super(Relic, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.value = 2
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Relic, self).onPlay(player, **kwargs)
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		player.minusDraw = True
			
class RoyalCarriage(Action, Reserve, CardAdd):
	name = 'Royal Carriage'
	def __init__(self, session, **kwargs):
		super(RoyalCarriage, self).__init__(session, **kwargs)
		self.triggerSignal = 'playAction'
		self.price = 5
		self.links = []
	def onPlay(self, player, **kwargs):
		super(RoyalCarriage, self).onPlay(player, **kwargs)
		self.links = []
		player.addAction()
	def call(self, signal, **kwargs):
		super(RoyalCarriage, self).call(signal, **kwargs)
		self.links.append(kwargs['card'])
		self.owner.session.dp.connect(self.destroyTrigger, signal='destroy')
		self.owner.playAction(kwargs['card'])
	def onDestroy(self, player, **kwargs):
		if self.links: return True
	def onLeavePlay(self, player, **kwargs):
		if self.links: player.session.dp.disconnect(self.destroyTrigger, signal='destroy')
	def destroyTrigger(self, signal, **kwargs):
		if kwargs['card']==self: return
		for i in range(len(self.links)-1, -1, -1):
			if self.links[i]==kwargs['card']: self.links.pop(i)
		if self.links: return
		self.owner.destroy(self)
				
class Storyteller(Action, CardAdd):
	name = 'Storyteller'
	def __init__(self, session, **kwargs):
		super(Storyteller, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Storyteller, self).onPlay(player, **kwargs)
		player.addAction()
		player.addCoin()
		for i in range(3):
			if not player.hand: break
			choice = player.user([o.name for o in player.hand]+['End Story Telling'], 'Choose treasure')
			if choice+1>len(player.hand): break
			if 'TREASURE' in player.hand[choice].types:
				playedTreasure = player.hand.pop(choice)
				player.inPlay.append(playedTreasure)
				player.playTreasure(playedTreasure)
		player.draw(amnt=player.coins)
		player.coins = 0
			
class SwampHag(Action, Attack, Duration, CardAdd):
	name = 'Swamp Hag'
	def __init__(self, session, **kwargs):
		super(SwampHag, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 5
		self.attacking = []
	def onPlay(self, player, **kwargs):
		super(SwampHag, self).onPlay(player, **kwargs)
		self.attacking = []
		player.session.dp.connect(self.trigger, signal='buy')
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self)
	def onLeavePlay(self, player, **kwargs):
		player.session.dp.disconnect(self.trigger, signal='buy')
	def trigger(self, signal, **kwargs):
		if not kwargs['player'] in self.attacking: return
		kwargs['player'].gainFromPile(kwargs['player'].session.piles['Curse'])
	def attack(self, player, **kwargs):
		kwargs['card'].attacking.append(player)
	def next(self, **kwargs):
		self.owner.addCoin(amnt=3)

class TreasureTrove(Treasure, CardAdd):
	name = 'Treasure Trove'
	def __init__(self, session, **kwargs):
		super(TreasureTrove, self).__init__(session, **kwargs)
		self.value = 2
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(TreasureTrove, self).onPlay(player, **kwargs)
		player.gainFromPile(player.session.piles['Copper'])
		player.gainFromPile(player.session.piles['Gold'])
		
class WineMerchant(Action, Reserve, CardAdd):
	name = 'Wine Merchant'
	def __init__(self, session, **kwargs):
		super(WineMerchant, self).__init__(session, **kwargs)
		Reserve.__init__(self, session, **kwargs)
		self.triggerSignal = 'endTurn'
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(WineMerchant, self).onPlay(player, **kwargs)
		player.addCoin(amnt=4)
		player.addBuy()
	def requirements(self, **kwargs):
		return self.owner==kwargs['player'] and self.owner.coins>1

class Hireling(Action, Duration, CardAdd):
	name = 'Hireling'
	def __init__(self, session, **kwargs):
		super(Hireling, self).__init__(session, **kwargs)
		Duration.__init__(self, session, **kwargs)
		self.price = 6
	def onPlay(self, player, **kwargs):
		player.session.dp.connect(self.next, signal='startTurn')
	def next(self, **kwargs):
		if not kwargs['player']==self.owner: return
		self.owner.draw()
	def onDestroy(self, player, **kwargs):
		return True
		
adventures = [CoinOfTheRealm, Page, Peasant, Ratcatcher, Raze, Amulet, CaravanGuard, Dungeon, Gear, Guide, Duplicate, Magpie, Messenger, Miser, Port, Ranger, Transmogrify, Artificer, BridgeTroll, DistantLands, Giant, HauntedWoods, LostCity, Relic, RoyalCarriage, Storyteller, SwampHag, TreasureTrove, WineMerchant, Hireling]

class Potion(Treasure, CardAdd):
	name = 'Potion'
	def __init__(self, session, **kwargs):
		super(Potion, self).__init__(session, **kwargs)
		self.value = 0
		self.potionValue = 1
		self.price = 4
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(16):
			pile.append(type(self)(session))
			
class Herbalist(Action, CardAdd):
	name = 'Herbalist'
	def __init__(self, session, **kwargs):
		super(Herbalist, self).__init__(session, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Herbalist, self).onPlay(player, **kwargs)
		player.addCoin()
		player.addBuy()
		player.session.dp.connect(self.trigger, signal='endTurn')
	def trigger(self, signal, **kwargs):
		options = set()
		for card in self.owner.inPlay:
			if 'TREASURE' in card.types: options.add(card.name)
		if not options: return
		options = list(options)
		choice = self.owner.user(options+['No top'], 'Choose top treasure')
		if choice+1>len(options): return
		for i in range(len(self.owner.inPlay)):
			if self.owner.inPlay[i].name==options[choice]:
				self.owner.library.append(self.owner.inPlay.pop(i))
				break
	def onLeavePlay(self, player, **kwargs):
		player.session.dp.disconnect(self.trigger, signal='endTurn')
		
class Apprentice(Action, CardAdd):
	name = 'Apprentice'
	def __init__(self, session, **kwargs):
		super(Apprentice, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Apprentice, self).onPlay(player, **kwargs)
		player.addAction()
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		coinVal, potionVal = player.hand[choice].getPrice(player), player.hand[choice].getPotionPrice(player)
		player.trash(choice)
		if potionVal>0: coinVal += 2
		player.draw(amnt=coinVal)
		
class Transmute(Action, CardAdd):
	name = 'Transmute'
	def __init__(self, session, **kwargs):
		super(Transmute, self).__init__(session, **kwargs)
		self.price = 0
		self.potionPrice = 1
	def onPlay(self, player, **kwargs):
		super(Transmute, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		types = player.hand[choice].types
		player.trash(choice)
		if 'ACTION' in types: player.gainFromPile(player.session.piles['Duchy'])
		if 'TREASURE' in types: player.gainFromPile(player.session.piles['Transmute'])
		if 'VICTORY' in types: player.gainFromPile(player.session.piles['Gold'])
	def onPileCreate(self, pile, session, **kwargs):
		super(Transmute, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)

class Vineyard(Victory, CardAdd):
	name = 'Vineyard'
	def __init__(self, session, **kwargs):
		super(Vineyard, self).__init__(session, **kwargs)
		self.price = 0
		self.potionPrice = 1
	def onGameEnd(self, player, **kwargs):
		actions = 0
		for card in player.library:
			if 'ACTION' in player.types: actions += 1
		player.addVictory(amnt=math.floor(actions/3))
	def onPileCreate(self, pile, session, **kwargs):
		super(Vineyard, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)

class Apothecary(Action, CardAdd):
	name = 'Apothecary'
	def __init__(self, session, **kwargs):
		super(Apothecary, self).__init__(session, **kwargs)
		self.price = 2
		self.potionPrice = 1
	def onPlay(self, player, **kwargs):
		super(Apothecary, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		cards = player.getCards(4)
		for i in range(len(cards)-1, -1, -1):
			player.reveal(cards[i])
			if cards[i].name=='Copper' or cards[i].name=='Potion': player.hand.append(cards.pop(i))
		while cards: player.library.append(cards.pop(player.user([o.name for o in cards], 'Put card back')))
	def onPileCreate(self, pile, session, **kwargs):
		super(Apothecary, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
		
class ScryingPool(Action, Attack, CardAdd):
	name = 'Scrying Pool'
	def __init__(self, session, **kwargs):
		super(ScryingPool, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 2
		self.potionPrice = 1
	def onPlay(self, player, **kwargs):
		super(ScryingPool, self).onPlay(player, **kwargs)
		player.addAction()
		for aplayer in player.session.getPlayers(player):
			aplayer.attack(self.attack, self, controller=player)
		cards = []
		while True:
			card = player.getCard()
			if not card: break
			player.reveal(card)
			cards.append(card)
			if not 'ACTION' in card.types: break
		while cards: player.hand.append(cards.pop())
	def attack(self, player, **kwargs):
		if not player.revealPosition(-1, fromZ=player.library): return
		if kwargs['controller'].user(('Top', 'Discard'), 'Choose card location'):
			player.session.dp.send(signal='scryingPoolDiscard')
			player.discardCard(player.library.pop())
		else:
			player.session.dp.send(signal='scryingPoolTop')
	def onPileCreate(self, pile, session, **kwargs):
		super(ScryingPool, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
			
class University(Action, CardAdd):
	name = 'University'
	def __init__(self, session, **kwargs):
		super(University, self).__init__(session, **kwargs)
		self.price = 2
		self.potionPrice = 1
	def onPlay(self, player, **kwargs):
		super(University, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		options = []
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and player.session.piles[pile].viewTop().getPrice(player)<6 and player.session.piles[pile].viewTop().getPotionPrice(player)<1 and player.session.piles[pile].viewTop().getDebtPrice(player)<1 and 'ACTION' in player.session.piles[pile].viewTop().types:
				options.append(pile)
		if not options: return
		choice = player.user(options+['No gain'], 'Choose gain')
		if choice+1>len(options): return
		player.gainFromPile(player.session.piles[options[choice]])
	def onPileCreate(self, pile, session, **kwargs):
		super(University, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
		
class Alchemist(Action, CardAdd):
	name = 'Alchemist'
	def __init__(self, session, **kwargs):
		super(Alchemist, self).__init__(session, **kwargs)
		self.price = 3
		self.potionPrice = 1
	def onPlay(self, player, **kwargs):
		super(Alchemist, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw(amnt=2)
	def onPileCreate(self, pile, session, **kwargs):
		super(Alchemist, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
	def onDestroy(self, player, **kwargs):
		hasPotion = False
		for card in player.inPlay:
			if card.name=='Potion':
				hasPotion = True
				break
		if not hasPotion: return
		if not player.user(('discard', 'top'), 'Alchemist'): return
		for i in range(len(player.inPlay)):
			if player.inPlay[i]==self:
				player.library.append(player.inPlay.pop(i))
				return True

class Familiar(Action, Attack, CardAdd):
	name = 'Familiar'
	def __init__(self, session, **kwargs):
		super(Familiar, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 3
		self.potionPrice = 1
	def onPlay(self, player, **kwargs):
		super(Familiar, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self, controller=player)
	def attack(self, player, **kwargs):
		player.gainFromPile(player.session.piles['Curse'])
	def onPileCreate(self, pile, session, **kwargs):
		super(Familiar, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
		
class PhilosophersStone(Treasure, CardAdd):
	name = "Philosopher's Stone"
	def __init__(self, session, **kwargs):
		super(PhilosophersStone, self).__init__(session, **kwargs)
		self.price = 3
		self.potionPrice = 1
	def onPlay(self, player, **kwargs):
		player.addCoin(amnt=m.floor((len(player.library)+len(player.discardPile))/5))
	def onPileCreate(self, pile, session, **kwargs):
		super(PhilosophersStone, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
			
class Golemn(Action, CardAdd):
	name = 'Golemn'
	def __init__(self, session, **kwargs):
		super(Golemn, self).__init__(session, **kwargs)
		self.price = 4
		self.potionPrice = 1
	def onPlay(self, player, **kwargs):
		super(Golemn, self).onPlay(player, **kwargs)
		actions = []
		revealed = []
		while len(actions)<2:
			card = player.getCard()
			if not card: break
			player.reveal(card)
			if 'ACTION' in card.types and card.name!='Golemn': actions.append(card)
			else: revealed.append(card)
		while revealed: player.discardCard(revealed.pop())
		while actions: player.playAction(actions.pop(player.user([o.name for o in actions], 'Choose action')))
	def onPileCreate(self, pile, session, **kwargs):
		super(Golemn, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
			
class Possession(Action, CardAdd):
	name = 'Possession'
	def __init__(self, session, **kwargs):
		super(Possession, self).__init__(session, **kwargs)
		self.price = 6
		self.potionPrice = 1
		self.possesed = None
		self.posseser = None
		self.trashed = []
	def onPlay(self, player, **kwargs):
		super(Possession, self).onPlay(player, **kwargs)
		player.session.delayedActions.append((self.possesionTurn, {'player': player.session.getNextPlayer(player), 'posseser': player}))
	def trashTrigger(self, signal, **kwargs):
		if kwargs['player']==self.possesed:
			self.trashed.append(kwargs['card'])
			return True
	def gainTrigger(self, signal, **kwargs):
		if kwargs['player']==self.possesed:
			self.posseser.gain(kwargs['card'], kwargs['source'])
			return True
	def possesionTurn(self, **kwargs):
		self.possesed = kwargs['player']
		self.posseser = kwargs['posseser']
		oriUser = self.possesed.user
		self.possesed.user = self.posseser.user
		self.owner.session.dp.connect(self.gainTrigger, signal='gain')
		self.owner.session.dp.connect(self.trashTrigger, signal='trash')
		self.possesed.session.activePlayer = self.possesed
		self.possesed.session.turnFlag = 'possession'
		self.possesed.resetValues()
		self.possesed.session.dp.send(signal='startTurn', player=self.possesed, flags=self.owner.session.turnFlag)
		self.possesed.actionPhase()
		self.possesed.treasurePhase()
		self.possesed.buyPhase()
		self.possesed.endTurn()
		self.possesed.user = oriUser
		while self.trashed: self.possesed.discardPile.append(self.trashed.pop())
		self.owner.session.dp.disconnect(self.trashTrigger, signal='trash')
		self.owner.session.dp.disconnect(self.gainTrigger, signal='gain')
	def onPileCreate(self, pile, session, **kwargs):
		super(Possession, self).onPileCreate(pile, session, **kwargs)
		session.requirePile(Potion)
	
alchemy = [Herbalist, Apprentice, Transmute, Vineyard, Apothecary, ScryingPool, University, Alchemist, Familiar, PhilosophersStone, Golemn, Possession]

class Crossroads(Action, CardAdd):
	name = 'Crossroads'
	def __init__(self, session, **kwargs):
		super(Crossroads, self).__init__(session, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Crossroads, self).onPlay(player, **kwargs)
		victories = 0
		for card in player.hand:
			player.revealCard(card)
			if 'VICTORY' in card.types: victories += 1
		player.draw(amnt=victories)
		crosses = 0
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[0]=='playAction' and player.session.events[1]['card'].name=='Crossroads':
				crosses += 1
				if crosses>1: return
			elif player.session.events[0]=='startTurn': break
		player.addAction(amnt=3)
		
class Duchess(Action, CardAdd):
	name = 'Duchess'
	def __init__(self, session, **kwargs):
		super(Duchess, self).__init__(session, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Duchess, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		for aplayer in player.session.getPlayers(player):
			card = aplayer.getCard()
			if not card: continue
			aplayer.reveal(card, hidden=aplayer)
			if aplayer.user(('discard', 'top'), 'Choose position'): aplayer.library.append(card)
			else: aplayer.discardCard(card)
	def trigger(self, signal, **kwargs):
		if kwargs['card'].name=='Duchy' and not kwargs['player'].user(('yes', 'no'), 'Choose gain Duchess'): kwargs['player'].gainFromPile(kwargs['player'].session.piles['Duchess'])
	def onPileCreate(self, pile, session, **kwargs):
		super(Duchess, self).onPileCreate(pile, session, **kwargs)
		session.dp.connect(self.trigger, signal='gain')

class FoolsGold(Treasure, Reaction, CardAdd):
	name = "Fool's Gold"
	def __init__(self, session, **kwargs):
		super(FoolsGold, self).__init__(session, **kwargs)
		Reaction.__init__(self, session, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(FoolsGold, self).onPlay(player, **kwargs)
		fools = 0
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[0]=='playTreasure' and player.session.events[1]['card'].name=='FoolsGold':
				fools += 1
				if fools>1:
					player.addCoin(amnt=4)
					return
			elif player.session.events[0]=='startTurn': break
		player.addCoin()
	def trigger(self, signal, **kwargs):
		if kwargs['card'].name=='Province' and not self.owner.user(('yes', 'no'), "trash fool's gold"):
			for i in range(len(self.owner.hand)-1, -1, -1):
				if self.owner.hand[i]==self:
					self.owner.trash(i)
					self.owner.gainFromPile(self.owner.session.piles['Gold'])
	def connect(self, **kwargs):
		kwargs['player'].session.dp.connect(self.trigger, signal='gain')
	def disconnect(self, **kwargs):
		kwargs['player'].session.dp.disconnect(self.trigger, signal='gain')
	def onGain(self, player, **kwargs):
		self.connect(player=player)
	def onTrash(self, player, **kwargs):
		self.disconnect(player=player)
	def onReturn(self, player, **kwargs):
		self.disconnect(player=player)
		
class Develop(Action, CardAdd):
	name = 'Develop'
	def __init__(self, session, **kwargs):
		super(Develop, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Develop, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		coinVal, potionVal, debtVal = player.hand[choice].getPrice(player), player.hand[choice].getPotionPrice(player), player.hand[choice].getPrice(player)
		player.trash(choice)
		if player.user(('Low first', 'High first'), 'Choose gain order'):
			self.gain(player, coinVal+1, potionVal, debtVal)
			self.gain(player, coinVal-1, potionVal, debtVal)
		else:
			self.gain(player, coinVal-1, potionVal, debtVal)
			self.gain(player, coinVal+1, potionVal, debtVal)
	def gain(self, player, cv, pv, dv, **kwargs):
		options = []
		for pile in player.session.piles:
			if player.session.piles[pile].viewTop() and player.session.piles[pile].viewTop().getPrice(player)==cv and player.session.piles[pile].viewTop().getPotionPrice(player)==pv and player.session.piles[pile].viewTop().getDebtPrice(player)==dv: options.append(pile)
		if not options: return
		choice = player.user(options, 'Choose gain')
		player.gainFromPile(player.session.piles[options[choice]], to=player.library)

class Oasis(Action, CardAdd):
	name = 'Oasis'
	def __init__(self, session, **kwargs):
		super(Oasis, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Oasis, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		player.addCoin()
		if not player.hand: return
		player.discard(player.user([o.name for o in player.hand], 'Choose discard'))

class Oracle(Action, Attack, CardAdd):
	name = 'Oracle'
	def __init__(self, session, **kwargs):
		super(Oracle, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Oracle, self).onPlay(player, **kwargs)
		for aplayer in player.session.getPlayers(player):
			aplayer.attack(self.attack, self, controller=player)
		player.draw(amnt=2)
	def attack(self, player, **kwargs):
		cards = player.getCards(2)
		if not cards: return
		for card in cards: player.reveal(card)
		if kwargs['controller'].user(('Top', 'Discard'), 'Choose card location'):
			while cards: player.discardCard(cards.pop())
		else:
			while cards: player.library.append(cards.pop(player.user([o.name for o in cards], 'Choose top order')))

class Scheme(Action, CardAdd):
	name = 'Scheme'
	def __init__(self, session, **kwargs):
		super(Scheme, self).__init__(session, **kwargs)
		self.price = 3
		self.scheming = []
		self.nexts = []
	def onPlay(self, player, **kwargs):
		super(Scheme, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		self.nexts.append(self.next)
		player.session.dp.connect(self.endTurnTrigger, signal='endTurn')
		player.session.dp.connect(self.destroyTrigger, signal='destroy')
		player.session.dp.connect(self.turnEndedTrigger, signal='turnEnded')
	def endTurnTrigger(self, signal, **kwargs):
		if not kwargs['player']==self.owner: return
		while self.nexts: self.nexts.pop()()
	def next(self, **kwargs):
		options = []
		for card in self.owner.inPlay:
			if 'ACTION' in card.types and not (hasattr(card, 'schemed') and card.schemed): options.append(card)			
		if not options: return
		choice = self.owner.user([o.name for o in options]+['No Scheme'], 'Choose scheme')
		if choice+1>len(options): return
		options[choice].schemed = True
		self.scheming.append(options[choice])
	def destroyTrigger(self, signal, **kwargs):
		if not kwargs['card'] in self.scheming: return
		for i in range(len(self.owner.inPlay)):
			print(self.owner.inPlay[i])
			if self.owner.inPlay[i]==kwargs['card']:
				self.owner.inPlay[i].onLeavePlay(self.owner)
				self.owner.library.append(self.owner.inPlay.pop(i))
				return True
	def turnEndedTrigger(self, signal, **kwargs):
		for scheme in self.scheming: scheme.schemed = False
		self.scheming[:] = []
		self.owner.session.dp.disconnect(self.endTurnTrigger, signal='endTurn')
		self.owner.session.dp.disconnect(self.destroyTrigger, signal='destroy')
		self.owner.session.dp.disconnect(self.turnEndedTrigger, signal='turnEnded')
	
class Tunnel(Victory, Reaction, CardAdd):
	name = 'Tunnel'
	def __init__(self, session, **kwargs):
		super(Tunnel, self).__init__(session, **kwargs)
		Reaction.__init__(self, session, **kwargs)
		self.price = 3
		self.value = 2
		self.signal = 'discard'
	def trigger(self, signal, **kwargs):
		if kwargs['card']==self and self.owner.user(('no', 'yes'), 'Reveal Tunnel'):
			self.owner.reveal(self)
			self.owner.gainFromPile(self.owner.session.piles['Gold'])
	def onGain(self, player, **kwargs):
		self.connect(player=player)
	def onTrash(self, player, **kwargs):
		self.disconnect(player=player)
	def onReturn(self, player, **kwargs):
		self.disconnect(player=player)

class JackOfAllTrades(Action, CardAdd):
	name = 'Jack of all Trades'
	def __init__(self, session, **kwargs):
		super(JackOfAllTrades, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(JackOfAllTrades, self).onPlay(player, **kwargs)
		player.gainFromPile(player.session.piles['Silver'])
		card = player.getCard()
		if card:
			player.reveal(card, hidden=player)
			if player.user(('discard', 'top'), 'Choose location'): player.library.append(card)
			else: player.discardCard(card)
		while len(player.hand)<6 and player.draw(): pass
		options = []
		for card in player.hand:
			if not 'TREASURE' in card.types: options.append(card)
		if not options: return
		choice = player.user([o.name for o in options]+['No trash'], 'Choose trash')
		if choice+1>len(options): return
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]:
				player.trash(i)
				return

class NobleBrigand(Action, Attack, CardAdd):
	name = 'Noble Brigand'
	def __init__(self, session, **kwargs):
		super(NobleBrigand, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 4
		session.dp.connect(self.trigger, signal='buy')
	def onPlay(self, player, **kwargs):
		super(NobleBrigand, self).onPlay(player, **kwargs)
		player.addCoin()
		self.attackOpponents(players)
	def attackOpponents(self, player, **kwargs):
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.attack(self.attack, self)
	def attack(self, player, **kwargs):
		cards = player.getCards(2)
		if not cards: return
		if not any('TEASURE' in o.types for o in cards):
			player.gainFromPile(player.session.piles['Copper'])
			return
		options = []
		for card in cards:
			if card.name in ('Gold', 'Silver'): options.append(card)
		if not options: return
		choice = self.owner.user([o.name for o in options], 'Choose steal')
		trashedCard = options.pop(choice)
		player.trashCard(trashedCard)
		self.owner.gain(trashedCard, player.session.trash)
		while cards: player.discardCard(card.pop())
	def trigger(self, signal, **kwargs):
		if 'pile' in kwargs and not self==kwargs['pile'].viewTop(): return
		self.attackOpponents(kwargs['player'])

class NomadCamp(Action, CardAdd):
	name = 'Nomad Camp'
	def __init__(self, session, **kwargs):
		super(NomadCamp, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(NomadCamp, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		player.addBuy()
	def onGain(self, player, **kwargs):
		for i in range(len(player.discardPile)-1, -1, -1):
			if player.discardPile[i]==self:
				player.library.append(player.discardPile.pop(i))
				break

class SilkRoad(Victory, CardAdd):
	name = 'Silk Road'
	def __init__(self, session, **kwargs):
		super(SilkRoad, self).__init__(session, **kwargs)
		self.price = 4
	def onGameEnd(self, player, **kwargs):
		victories = 0
		for card in player.library:
			if 'VICTORY' in card.types: victories += 1
		player.addVictory(amnt=m.floor(victories/4))

class SpiceMerchant(Action, CardAdd):
	name = 'SpiceMerchant'
	def __init__(self, session, **kwargs):
		super(SpiceMerchant, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(SpiceMerchant, self).onPlay(player, **kwargs)
		options = []
		for card in player.hand:
			if 'TREASURE' in card.types: options.append(card)
		if not options: return
		choice = player.user([o.name for o in options]+['No trash'], 'Choose trash')
		if choise+1>len(options): return
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]: player.trash(i)
		if player.user(('coins and buy', 'cards and action'), 'Choose benefit'):
			player.draw(amnt=2)
			player.addAction()
		else:
			player.addCoin(amnt=2)
			player.addBuy()

class Trader(Action, Reaction, CardAdd):
	name = 'Trader'
	def __init__(self, session, **kwargs):
		super(Trader, self).__init__(session, **kwargs)
		Reaction.__init__(self, session, **kwargs)
		self.price = 4
		self.signal = 'tryGain'
	def onPlay(self, player, **kwargs):
		super(Trader, self).onPlay(player, **kwargs)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		coinVal = player.hand[choice].getPrice(player)
		player.trash(choice)
		for i in range(coinVal): player.gainFromPile(player.session.piles['Silver'])
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and not kwargs['card'].name=='Silver' and self in self.owner.hand and self.owner.user(('no', 'yes'), 'Use Trader'):
			self.owner.reveal(self)
			self.owner.gainFromPile(self.owner.session.piles['Silver'])
			return True
	def onGain(self, player, **kwargs):
		self.connect(session=player.session)
	def onTrash(self, player, **kwargs):
		self.disconnect(session=player.session)
	def onReturn(self, player, **kwargs):
		self.disconnect(session=player.session)

class Cache(Treasure, CardAdd):
	name = 'Cache'
	def __init__(self, session, **kwargs):
		super(Cache, self).__init__(session, **kwargs)
		self.value = 3
		self.price = 5
	def onGain(self, player, **kwargs):
		for i in range(2): player.gainFromPile(player.session.piles['Copper'])

class Cartographer(Action, CardAdd):
	name = 'Cartographer'
	def __init__(self, session, **kwargs):
		super(Cartographer, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Cartographer, self).onPlay(player, **kwargs)
		player.draw()
		player.addAction()
		cards = player.getCards(4)
		if not cards: return
		while cards:
			choice = player.user([o.name for o in cards]+['No discard'], 'Choose discard')
			if choice+1>len(cards): break
			player.discardCard(cards.pop(choice))
		while cards: player.library.append(cards.pop(player.user([o.name for o in cards], 'Choose top')))

class Embassy(Action, CardAdd):
	name = 'Embassy'
	def __init__(self, session, **kwargs):
		super(Embassy, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Embassy, self).onPlay(player, **kwargs)
		player.draw(amnt=5)
		for i in range(3):
			if not player.hand: return
			player.discard(player.user([o.name for o in player.hand], 'Choose discard'))
	def onGain(self, player, **kwargs):
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.gainFromPile(player.session.piles['Silver'])

class Haggler(Action, CardAdd):
	name = 'Haggler'
	def __init__(self, session, **kwargs):
		super(Haggler, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(Haggler, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		self.connect()
	def onLeavePlay(self, player, **kwargs):
		self.disconnect()
	def trigger(self, signal, **kwargs):
		if not kwargs['player']==self.owner: return
		options = []
		for pile in self.owner.session.piles:
			if not self.owner.session.piles[pile].viewTop(): continue
			option = self.owner.session.piles[pile].viewTop()
			if option.costLessThan(kwargs['card'], self.owner): options.append(pile)
		if not options: return
		choice = self.owner.user(options, 'Choose gain')
		self.owner.gainFromPile(self.owner.session.piles[options[choice]])
	def connect(self, **kwargs):
		self.owner.session.dp.connect(self.trigger, signal='buy')
	def disconnect(self, **kwargs):
		self.owner.session.dp.disconnect(self.trigger, signal='buy')

class Highway(Action, CardAdd):
	name = 'Highway'
	def __init__(self, session, **kwargs):
		super(Highway, self).__init__(session, **kwargs)
		self.price = 5
		self.reduction = 0
	def onPlay(self, player, **kwargs):
		super(Highway, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
		self.reduce()
	def onLeavePlay(self, player, **kwargs):
		self.inflate()
	def reduce(self):
		if self.reduction>0: return
		self.reduction += 1
		for card in self.owner.session.allCards: card.price -= 1
	def inflate(self):
		for card in self.owner.session.allCards: card.price += self.reduction
		self.reduction = 0

class IllGottenGains(Treasure, CardAdd):
	name = 'Ill-Gotten Gains'
	def __init__(self, session, **kwargs):
		super(IllGottenGains, self).__init__(session, **kwargs)
		self.price = 5
		self.value = 1
	def onPlay(self, player, **kwargs):
		super(IllGottenGains, self).onPlay(player, **kwargs)
		if player.user(['No', 'Yes'], 'Gain copper'): player.gainFromPile(player.session.piles['Copper'], to=player.hand)
	def onGain(self, player, **kwargs):
		for aplayer in player.session.getPlayers(player):
			if not aplayer==player: aplayer.gainFromPile(player.session.piles['Curse'])
		
hinterlands = [Crossroads, Duchess, FoolsGold, Develop, Oasis, Oracle, Scheme, Tunnel, JackOfAllTrades, NobleBrigand, NomadCamp, SilkRoad, SpiceMerchant, Trader, Cache, Cartographer, Embassy, Haggler, Highway, IllGottenGains]

class CityQuarter(Action, CardAdd):
	name = 'City Quarter'
	def __init__(self, session, **kwargs):
		super(CityQuarter, self).__init__(session, **kwargs)
		self.debtPrice = 8
	def onPlay(self, player, **kwargs):
		super(CityQuarter, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		actions = 0
		for card in player.hand:
			player.reveal(card)
			if 'ACTION' in card.types: actions += 1
		player.draw(amnt=actions)
		
class RoyalBlacksmith(Action, CardAdd):
	name = 'Royal Blacksmith'
	def __init__(self, session, **kwargs):
		super(RoyalBlacksmith, self).__init__(session, **kwargs)
		self.debtPrice = 8
	def onPlay(self, player, **kwargs):
		super(RoyalBlacksmith, self).onPlay(player, **kwargs)
		player.draw(amnt=5)
		actions = 0
		for i in range(len(player.hand)-1, -1, -1):
			player.reveal(player.hand[i])
			if player.hand[i].name=='Copper': player.discard(i)
			
class Capital(Treasure, CardAdd):
	name = 'Capital'
	def __init__(self, session, **kwargs):
		super(Capital, self).__init__(session, **kwargs)
		self.price = 5
		self.value = 6
	def onPlay(self, player, **kwargs):
		super(Capital, self).onPlay(player, **kwargs)
		player.addBuy()
	def onDestroy(self, player, **kwargs):
		player.addDebt(amnt=6)
		player.payDebt()
		
class Villa(Action, CardAdd):
	name = 'Villa'
	def __init__(self, session, **kwargs):
		super(Villa, self).__init__(session, **kwargs)
		self.price = 4
	def onPlay(self, player, **kwargs):
		super(Villa, self).onPlay(player, **kwargs)
		player.addAction(amnt=2)
		player.addCoin()
		player.addBuy()
	def onGain(self, player, **kwargs):
		player.addAction()
		index = kwargs['source'].index(self)
		if index: player.hand.append(kwargs['source'].pop(index))
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='actionPhase' or player.session.events[i][0]=='treasurePhase': break
			elif player.session.events[i][0]=='buyPhase' and player.session.events[i][1]['player']==player:
				player.actionPhase()
				player.treasurePhase()
				player.buyPhase()
				break
		return True
		
class Gladiator(Action, CardAdd):
	name = 'Gladiator'
	def __init__(self, session, **kwargs):
		super(Gladiator, self).__init__(session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Gladiator, self).onPlay(player, **kwargs)
		player.addCoin(amnt=2)
		if not player.hand: return
		choice = player.user([o.name for o in player.hand], 'Choose reveal')
		player.reveal(player.hand[choice])
		splayer = player.session.getNextPlayer(player)
		schoice = splayer.user([o.name for o in splayer.hand]+['No reveal'], 'Choose reveal')
		if not schoice+1>len(splayer.hand): splayer.reveal(splayer.hand[schoice])
		if schoice+1>len(splayer.hand) or splayer.hand[schoice]!=player.hand[choice]:
			player.addCoin()
			if player.session.piles['Gladiator/Fortune'].viewTop() and player.session.piles['Gladiator/Fortune'].viewTop().name=='Gladiator': player.trashCard(player.session.piles['Gladiator/Fortune'].gain())
		
class Fortune(Treasure, CardAdd):
	name = 'Fortune'
	def __init__(self, session, **kwargs):
		super(Fortune, self).__init__(session, **kwargs)
		self.price = 8
		self.debtPrice = 8
	def onPlay(self, player, **kwargs):
		super(Fortune, self).onPlay(player, **kwargs)
		player.addBuy()
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='doubleMoney' and player.session.events[i][1]['player']==player: return
			elif player.session.events[i][0]=='startTurn': break
		player.session.dp.send('doubleMoney', player=self)
		player.addCoin(amnt=player.coins)
	def onGain(self, player, **kwargs):
		for card in player.inPlay:
			if card.name=='Gladiator': player.gainFromPile(player.session.piles['Gold'])
			
class GladiatorFortune(Card, CardAdd):
	name = 'Gladiator/Fortune'
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(5): pile.append(Fortune(session))
		for i in range(5): pile.append(Gladiator(session))
		
class Settlers(Action, CardAdd):
	name = 'Settlers'
	def __init__(self, session, **kwargs):
		super(Settlers, self).__init__(session, **kwargs)
		self.price = 2
	def onPlay(self, player, **kwargs):
		super(Settlers, self).onPlay(player, **kwargs)
		player.addAction()
		player.draw()
		coppers = 0
		for card in player.discardPile:
			if card.name=='Copper': coppers+=1
		for i in range(player.user(list(range(min(coppers, 1)+1)), 'Choose amnount')):
			for n in range(len(player.discardPile)-1, -1, -1):
				if player.discardPile[n].name=='Copper':
					player.reveal(player.discardPile[n])
					player.hand.append(player.discardPile.pop(n))
					break
					
class BustlingVillage(Action, CardAdd):
	name = 'Bustling Village'
	def __init__(self, session, **kwargs):
		super(BustlingVillage, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(BustlingVillage, self).onPlay(player, **kwargs)
		player.addAction(amnt=3)
		player.draw()
		settlers = 0
		for card in player.discardPile:
			if card.name=='Settlers': settlers+=1
		for i in range(player.user(list(range(min(settlers, 1)+1)), 'Choose amnount')):
			for n in range(len(player.discardPile)-1, -1, -1):
				if player.discardPile[n].name=='Settlers':
					player.reveal(player.discardPile[n])
					player.hand.append(player.discardPile.pop(n))
					break
					
class SettlersBustlingVillage(Card, CardAdd):
	name = 'Settlers/BustlingVillage'
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(5): pile.append(BustlingVillage(session))
		for i in range(5): pile.append(Settlers(session))

class Catapult(Action, Attack, CardAdd):
	name = 'Catapult'
	def __init__(self, session, **kwargs):
		super(Catapult, self).__init__(session, **kwargs)
		Attack.__init__(self, session, **kwargs)
		self.price = 3
	def onPlay(self, player, **kwargs):
		super(Catapult, self).onPlay(player, **kwargs)
		player.addCoin()
		if not player.hand: return
		attacks = []
		choice = player.user([o.name for o in player.hand], 'Choose trash')
		if player.hand[choice].getPrice(player)>2: attacks.append(self.attackCurse)
		if 'TREASURE' in player.hand[choice].types: attakcs.append(self.attackDiscard)
		player.trash(choice)
		for aplayer in player.session.getPlayers(player):
			if aplayer==player: continue
			for attack in attacks: aplayer.attack(attack, self, controller=player)
	def attackCurse(self, player, **kwargs):
		player.gainFromPile(player.session.piles['Curse'])
	def attackDiscard(self, player, **kwargs):
		while len(player.hand)>3:
			choice = player.user([o.name for o in player.hand], 'Choose discard')
			player.discard(choice)
			
class Rocks(Treasure, CardAdd):
	name = 'Rocks'
	def __init__(self, session, **kwargs):
		super(Rocks, self).__init__(session, **kwargs)
		self.price = 4
	def gainSilver(self, player, **kwargs):
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='actionPhase' or player.session.events[i][0]=='treasurePhase': break
			elif player.session.events[i][0]=='buyPhase' and player.session.events[i][1]['player']==player:
				player.gainFromPile(player.session.piles[pile], to=player.library)
				return
		player.gainFromPile(player.session.piles[pile], to=player.hand)
	def onGain(self, player, **kwargs):
		self.gainSilver(player)
	def onTrash(self, player, **kwargs):
		self.gainSilver(player)
		
class CatapultRocks(Card, CardAdd):
	name = 'Catapult/Rocks'
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(5): pile.append(Rocks(session))
		for i in range(5): pile.append(Catapult(session))

class Crown(Action, Treasure, CardAdd):
	name = 'Crown'
	def __init__(self, session, **kwargs):
		super(Crown, self).__init__(session, **kwargs)
		Treasure.__init__(self, session, **kwargs)
		self.price = 5
		self.links = []
	def onPlay(self, player, **kwargs):
		super(Crown, self).onPlay(player, **kwargs)
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='actionPhase' and player.session.events[i][1]['player']==player:
				self.doublePlay(player, 'ACTION', **kwargs)
				return
			elif player.session.events[i][0]=='treasurePhase' and player.session.events[i][1]['player']==player:
				self.doublePlay(player, 'TREASURE', **kwargs)
				return
	def doublePlay(self, player, tp='ACTION', **kwargs):
		self.links = []
		options = []
		for card in player.hand:
			if tp in card.types:
				options.append(card)
		if not options: return
		choice = player.user([o.name for o in options], 'Choose '+tp)
		for i in range(len(player.hand)):
			if player.hand[i]==options[choice]:
				player.inPlay.append(player.hand.pop(i))
				break
		self.links.append(options[choice])
		player.session.dp.connect(self.trigger, signal='destroy')
		for i in range(2):
			if tp=='ACTION': player.playAction(options[choice])
			elif tp=='TREASURE': player.playTreasure(options[choice])
	def onDestroy(self, player, **kwargs):
		if self.links: return True
	def onLeavePlay(self, player, **kwargs):
		if self.links: player.session.dp.disconnect(self.trigger, signal='destroy')
	def trigger(self, signal, **kwargs):
		if kwargs['card']==self: return
		for i in range(len(self.links)-1, -1, -1):
			if self.links[i]==kwargs['card']: self.links.pop(i)
		if self.links: return
		self.owner.destroy(self)

class GroundsKeeper(Action, CardAdd):
	name = 'Grounds Keeper'
	def __init__(self, session, **kwargs):
		super(GroundsKeeper, self).__init__(session, **kwargs)
		self.price = 5
	def onPlay(self, player, **kwargs):
		super(GroundsKeeper, self).onPlay(player, **kwargs)
		self.connect()
		player.addAction()
		player.draw()
	def onLeavePlay(self, player, **kwargs):
		self.disconnect()
	def trigger(self, signal, **kwargs):
		if kwargs['player']==self.owner and 'VICTORY' in kwargs['card'].types: self.owner.addVictory()
	def connect(self, **kwargs):
		player.session.dp.connect(self.trigger, signal='buy')
	def disconnect(self, **kwargs):
		player.session.dp.disconnect(self.trigger, signal='buy')
		
empires = [CityQuarter, RoyalBlacksmith, Capital, Villa, GladiatorFortune, SettlersBustlingVillage, CatapultRocks, Crown, GroundsKeeper]