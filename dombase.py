from pydispatch import dispatcher as dp
import re
import math as m
import copy
import types
from events import *

class Log(object):
	def __init__(self, **kwargs):
		self.out = open('log.log', 'a')
	def log(self, *args, end='\n'):
		for arg in args:
			self.out.write(str(arg))
		self.out.write(end)

class CPile(list):
	def __init__(self, *args, **kwargs):
		super(CPile, self).__init__(*args)
		self.faceup = kwargs.get('faceup', True)
		self.private = kwargs.get('private', False)
		self.owner = kwargs.get('owner', None)
		self.ordered = kwargs.get('ordered', False)
		self.name = kwargs.get('name', True)
	def getFullView(self):
		ud = ''
		for item in set([o.view() for o in self]):
			ud += str([o.view() for o in self].count(item))+' '+item+', '
		return ud[:-1]
	def canSee(self, player=None):
		return not (not self.faceup or self.private and player!=self.owner)
	def getView(self, player=None):
		if self.canSee(player): return self.getFullView()
		else: return str(len(self))+' cards'
	
	def fullJView(self):
		return {'cards': [c.jview() for c in self]}
	def jview(self, player=None):
		if self.canSee(player): return self.fullJView()
		else: {'length': len(self)}
		
	def index(self, element):
		if not element in self: return None
		return super(CPile, self).index(element)
	def popx(self, pos=None):
		if self:
			if not pos==None: return self.pop(pos)
			else: return self.pop()
		else: return None
	def viewTop(self):
		if not self: return None
		return self[-1]

def gN(ob):
	if hasattr(ob, 'playerName'): return ob.playerName
	elif hasattr(ob, 'view'): return ob.view()
	elif hasattr(ob, 'name'): return ob.name
	elif hasattr(ob, 'getView'): return ob.getView()
	else: return str(ob)
	
def testUser(options):
	for option in options: print(gN(option), end=', ')
	choicePosition = -2
	while choicePosition<-1:
		choice = input(': ')
		if not choice: return len(options)-1
		for i in range(len(options)):
			if re.match(choice, gN(options[i]), re.IGNORECASE):
				choicePosition = i
				break
	return choicePosition

class Game(EventSession):
	def __init__(self, **kwargs):
		super(Game, self).__init__(**kwargs)
		self.trash = CPile(name='Trash')
		self.players = kwargs.get('players', [])
		self.piles = {}
		self.NSPiles = {}
		self.eventSupply = {}
		self.landmarks = {}
		self.activePlayer = None
		self.globalMats = {}
		self.emptyTerminatorPiles = 0
		self.events = []
		self.turnFlag = ''
		self.round = 0
		self.conceded = []
		self.extraTurns = []
		self.running = False
		self.replaceOrder = self.rReplaceOrder
		self.orderTriggers = self.rOrderTriggers
		self.endCondition = self.checkGameEnd
	def jpiles(self):
		return {key: self.piles[key].jview() for key in self.piles}
	def jNSPiles(self):
		return {key: self.NSPiles[key].jview() for key in self.NSPiles}
	def jdevents(self):
		return {key: self.eventSupply[key].jview() for key in self.eventSupply}
	def jlandmarks(self):
		return {key: self.landmarks[key].jview() for key in self.landmarks}
	def pilesView(self, player):
		ud = ''
		for key in sorted(self.piles): ud += self.piles[key].getView()+', '
		return ud
	def eventsView(self, player):
		ud = ''
		for key in sorted(self.eventSupply): ud += self.eventSupply[key].view()+', '
		return ud
	def landmarksView(self, player):
		ud = ''
		for key in sorted(self.landmarks): ud += self.landmarks[key].view()+', '
		return ud
	def NSPilesView(self, player):
		ud = ''
		for key in sorted(self.NSPiles): ud += self.NSPiles[key].getView()+', '
		return ud
	def requirePile(self, card, **kwargs):
		if card.name in list(self.piles): return
		self.piles[card.name] = Pile(card, self)
	def require(self, card, **kwargs):
		if card.name in list(self.NSPiles): return
		self.NSPiles[card.name] = Pile(card, self)
	def evLogger(self, signal, **kwargs):
		self.events.append((signal, kwargs))
	def evClean(self):
		self.resolveTriggerQueue()
	def fixNames(self, **kwargs):
		for player in self.players:
			while player.name in [p.name for p in self.players if not p==player]: player.name+='_'
	def start(self, **kwargs):
		self.running = True
		self.fixNames()
		self.round = 0
		self.dp.connect(self.evLogger)
		for player in self.players: self.dp.connect(player.toPlayer)
		self.dp.send(signal='globalSetup', players=self.players)
		self.resolveTriggerQueue()
		for player in self.players: player.setup(self)
		while self.running:
			self.round+=1
			self.dp.send(signal='beginRound', round=self.round)
			for player in self.players:
				if not self.takeTurn(player): return
				while self.extraTurns:
					et = self.extraTurns.pop(0)
					et[0](**et[1])
					if self.endCondition():
						self.endGame()
						return
	def takeTurn(self, player, **kwargs):
		player.takeTurn(**kwargs)
		if self.endCondition():
			self.endGame()
			return False
		return True
	def concede(self, player, **kwargs):
		self.conceded.append(player)
		self.endGame()
	def endGame(self):
		self.dp.send(signal='sessionEnding')
		for player in self.players: player.endGame()
		self.players.sort(key=lambda x: x.vp, reverse=True)
		points = {}
		for player in self.players: points[player.name] = player.vp
		winners=[item for item in self.players if not item in self.conceded]
		if not winners: winner = self.players[0]
		else: winner = winners[0]
		self.dp.send(signal='sessionEnd', winner=winner, points=points)
		for player in self.players: player.sessionEnd()
		self.running = False
	def getNextPlayer(self, cplayer):
		if not cplayer in self.players: return
		if not len(self.players)>1: return cplayer
		for i in range(len(self.players)):
			if self.players[i]==cplayer: return self.players[(i+1)%len(self.players)]	
	def getPreviousPlayer(self, cplayer):
		if not cplayer in self.players: return
		if not len(self.players)>1: return cplayer
		for i in range(len(self.players)):
			if self.players[i]==cplayer: return self.players[i-1]
	def getPlayers(self, cplayer):
		for i in range(len(self.players)):
			if self.players[i]==cplayer:
				yield cplayer
				n=(i+1)%len(self.players)
				while self.players[n]!=cplayer:
					yield self.players[n]
					n=(n+1)%len(self.players)
	def getOtherPlayers(self, cplayer):
		for i in range(len(self.players)):
			if self.players[i]==cplayer:
				n=(i+1)%len(self.players)
				while self.players[n]!=cplayer:
					yield self.players[n]
					n=(n+1)%len(self.players)
	def addGlobalMat(self, name):
		if not name in list(self.globalMats): self.globalMats[name] = CPile(name=name)
	def addMat(self, name, **kwargs):
		for player in self.players:
			if not name in list(player.mats): player.mats[name] = CPile(name=name, owner=player, **kwargs)
	def addToken(self, token):
		for player in self.players:
			if not token.name in player.tokens: self.resolveEvent(MakeToken, token=token(self), player=player)
	def getEmptyPiles(self):
		piles = []
		for key in self.piles:
			if not self.piles[key]: piles.append(self.piles[key])
		return piles
	def checkGameEnd(self):
		emptyPiles = 0
		for pile in self.piles:
			if not self.piles[pile]:
				if self.piles[pile].terminator:
					return True
				emptyPiles += 1
		if emptyPiles>=3: return True
		return False
	def makePiles(self, cards):
		for card in cards:
			self.piles[card.name] = Pile(card, self)
	def makeDEvents(self, events):
		for event in events: self.eventSupply[event.name] = event(self)
	def makeLandmarks(self, landmarks):
		for landmark in landmarks: self.landmarks[landmark.name] = landmark(self)
	def getPilesView(self):
		ud = ''
		for pile in self.piles: ud+=self.piles[pile].getView()+', '
		return ud
	def makeStartDeck(self):
		for player in self.players:
			for i in range(7): self.resolveEvent(TakeFromPile, frm=self.piles['Copper'], player=player)
			for i in range(3): self.resolveEvent(TakeFromPile, frm=self.piles['Estate'], player=player)
			#for i in range(2): self.resolveEvent(GainFromPile, frm=self.piles['Estate'], player=player)
			#for i in range(2): self.resolveEvent(TakeFromPile, frm=self.NSPiles['Teacher'], player=player)
	def rReplaceOrder(self, options):
		for player in self.getPlayers(self.activePlayer):
			os = [o for o in options if o.source.owner==player]
			if not os: continue
			return options.index(os[player.user([o.source.view() for o in os], 'Choose replacement')])
		return 0
	def rOrderTriggers(self, options):
		aoptions = copy.copy(options)
		ud = []
		for player in self.getPlayers(self.activePlayer):
			os = [aoptions.pop(aoptions.index(o)) for o in copy.copy(aoptions) if o[0].source.owner==player]
			while os: ud.append(os.pop(player.user([o[0].source.view() for o in os], 'Choose trigger '+str([o[0].source.view() for o in ud]))))
		ud.extend(aoptions)
		return ud
			
class Player(object):
	def __init__(self, **kwargs):
		self.coins = 0
		self.potions = 0
		self.actions = 0
		self.buys = 0
		self.victories = 0
		self.vp = 0
		self.debt = 0
		self.hand = CPile(name='hand', owner=self, private=True)
		self.library = CPile(name='library', owner=self, faceup=False, ordered=True)
		self.inPlay = CPile(name='inPlay', owner=self)
		self.discardPile = CPile(name='discardPile', owner=self)
		self.mats = {}
		self.tokens = {}
		self.user = testUser
		self.name = kwargs.get('name', 'p1')
		self.channelOut = None
		self.uiupdate = None
		self.uilog = copy.copy(self)
		self.session = None
		self.eotdraw = 5
		self.journey = True
		self.minusCoin = False
		self.minusDraw = False
		self.owner = self
		self.owns = CPile(name='owns', owner=self)
	def view(self, **kwargs):
		return self.name
	def resolveEvent(self, event, **kwargs):
		return self.session.resolveEvent(event, player=self, **kwargs)
	def jmats(self, player, **kwargs):
		return {key: self.mats[key].jview(player) for key in self.mats}
	def matsView(self, player, **kwargs):
		ud = ''
		for key in self.mats: ud += key+': '+self.mats[key].getView(player)+'\n'
		return ud
	def request(self, head):
		if head=='stat': return 'Actions: '+str(self.actions)+'\tCoins: '+str(self.coins)+'\tBuys: '+str(self.buys)
		elif head=='king':
			ud = ''
			for key in sorted(self.session.piles): ud+=key+' '+str(self.session.piles[key].maskot.coinPrice.access())+'$: '+str(len(self.session.piles[key]))+', '
			ud += '\n'
			for key in sorted(self.session.eventSupply): ud+=key+' '+str(self.session.eventSupply[key].coinPrice.access())+'$, '
			return ud
	def getStatView(self):
		self.calcVP()
		return 'Library: '+self.library.getView()+'\tHand: '+str(len(self.hand))+'\nActions: '+str(self.actions)+', VPT: '+str(self.victories)+', VP: '+str(self.vp)+', Journey: '+str(self.journey)+'\n$: '+str(self.coins)+', Buys: '+str(self.buys)+', P: '+str(self.potions)+', D: '+str(self.debt)+'\n-Coin: '+str(self.minusCoin)+'\t-Draw: '+str(self.minusDraw)
	def jvalues(self, **kwargs):
		return {
			'actions': self.actions,
			'vpt': self.victories,
			'vp': self.vp,
			'journey': self.journey,
			'coins': self.coins,
			'buys': self.buys,
			'potions': self.potions,
			'debt': self.debt,
			'minusCoin': self.minusCoin,
			'minusDraw':self.minusDraw
		}
	def getOpponentView(self, player, **kwargs):
		return self.inPlay.getView(), self.getStatView(), self.discardPile.getView(), self.matsView(player)
	def jview(self, player):
		return {
			'hand': self.hand.jview(player),
			'inPlay': self.inPlay.jview(player),
			'discardPile': self.discardPile.jview(player),
			'values': self.jvalues(),
			'mats': self.jmats(player)
		}
	def jsonUI(self):
		if not self==self.session.activePlayer and self.session.activePlayer: oppoV=self.session.activePlayer.getOpponentView(self)
		else: oppoV = self.session.getPreviousPlayer(self).getOpponentView(self)
		return {
			'player': self.jview(self),
			'trash': self.session.trash.jview(self),
			'kingdom':{
				'piles': self.session.jpiles(),
				'events': self.session.jdevents(),
				'landmarks': self.session.jlandmarks(),
				'nonSupplyPiles': self.session.jNSPiles()
			},
			'opponents': {p.name: p.jview(self) for p in self.session.getOtherPlayers(self)}
		 }
	def updateUI(self):
		self.uiupdate('play', 'hand', self.hand.getFullView())
		self.uiupdate('play', 'play', self.inPlay.getView())
		self.uiupdate('play', 'dcar', self.discardPile.getView())
		self.uiupdate('play', 'stat', self.getStatView())
		self.uiupdate('play', 'mats', self.matsView(self))
		self.uiupdate('tras', 'nnnn', self.session.trash.getView())
		self.uiupdate('play', 'stat', self.getStatView())
		self.uiupdate('king', 'pile', self.session.pilesView(self))
		self.uiupdate('king', 'even', self.session.eventsView(self)+'\n'+self.session.landmarksView(self))
		self.uiupdate('king', 'nspi', self.session.NSPilesView(self))
		if not self==self.session.activePlayer and self.session.activePlayer: oppoV=self.session.activePlayer.getOpponentView(self)
		else: oppoV = self.session.getPreviousPlayer(self).getOpponentView(self)
		self.uiupdate('oppo', 'play', oppoV[0])
		self.uiupdate('oppo', 'stat', oppoV[1])
		self.uiupdate('oppo', 'dcar', oppoV[2])
		self.uiupdate('oppo', 'mats', oppoV[3])
	def OLDtoPlayer(self, signal, **kwargs):
		if not self.channelOut: return
		eventWhiteList = ['Gain', 'Discard', 'Destroy', 'Trash', 'PlayCard', 'AddCoin', 'AddPotion', 'AddDebt', 'AddBuy', 'AddAction', 'AddVictory', 'Buy', 'BuyDEvent', 'Draw', 'PayDebt', 'Reveal', 'ResolveAttack', 'MoveToken', 'ResolveDuration', 'Message', 'DiscardDeck', 'AddToken', 'ReturnCard', 'PutBackCard', 'Take', 'TakeMinusDraw', 'TakeMinusCoin', 'FlipJourney']
		whiteList = ['treasurePhase', 'actionPhase', 'buyPhase', 'globalSetup', 'beginRound', 'setup', 'startTurn', 'endTurn', 'turnEnded', 'sessionEnd']
		keyBlackList = ['signal', 'source', 'session', 'hasReplaced', 'hidden', 'censored']
		keyWhiteList = ['card', 'frm', 'to', 'content', 'amnt', 'player', 'points', 'winner', 'flags', 'round']
		if signal in whiteList: s = [signal, {}]
		elif signal[-6:]=='_begin' and signal[:-6] in eventWhiteList: s = [signal[:-6], {}]
		else: return
		hidden = False
		censored = ['card']
		if 'hidden' in kwargs: hidden = kwargs['hidden']
		if 'censored' in kwargs: censored = kwargs['censored']
		for key in kwargs:
			if key in keyWhiteList and not (key in keyBlackList or (hidden and hidden!=self and key in censored) or (key=='card' and 'to' in kwargs and 'frm' in kwargs and not kwargs['to'].canSee(self) and not kwargs['frm'].canSee(self))): s[1][key] = gN(kwargs[key])
		if signal=='globalSetup': s[1]['you'] = self.name
		self.channelOut(s)
	def toPlayer(self, signal, **kwargs):
		if not self.channelOut: return
		eventWhiteList = ['Gain', 'Discard', 'Destroy', 'Trash', 'PlayCard', 'AddCoin', 'AddPotion', 'AddDebt', 'AddBuy', 'AddAction', 'AddVictory', 'Buy', 'BuyDEvent', 'Draw', 'PayDebt', 'Reveal', 'ResolveAttack', 'MoveToken', 'ResolveDuration', 'Message', 'DiscardDeck', 'AddToken', 'ReturnCard', 'PutBackCard', 'Take', 'TakeMinusDraw', 'TakeMinusCoin', 'FlipJourney']
		whiteList = ['treasurePhase', 'actionPhase', 'buyPhase', 'globalSetup', 'beginRound', 'setup', 'startTurn', 'endTurn', 'turnEnded', 'sessionEnd']
		keyBlackList = ['signal', 'source', 'session', 'hasReplaced', 'hidden', 'censored']
		keyWhiteList = ['card', 'frm', 'to', 'content', 'amnt', 'player', 'points', 'winner', 'flags', 'round']
		if signal in whiteList: s = [signal, {}]
		elif signal[-6:]=='_begin' and signal[:-6] in eventWhiteList: s = [signal[:-6], {}]
		else: return
		hidden = False
		censored = ['card']
		if 'hidden' in kwargs: hidden = kwargs['hidden']
		if 'censored' in kwargs: censored = kwargs['censored']
		for key in kwargs:
			if key in keyWhiteList and not (key in keyBlackList or (hidden and hidden!=self and key in censored) or (key=='card' and 'to' in kwargs and 'frm' in kwargs and not kwargs['to'].canSee(self) and not kwargs['frm'].canSee(self))): s[1][key] = gN(kwargs[key])
		#if signal=='globalSetup': s[1]['you'] = self.name
		self.channelOut(s[0], **s[1])
	def getView(self):
		return 'Hand: '+self.hand.getFullView()+'\nIn Play: '+self.inPlay.getView()+'\nDiscard: '+self.discardPile.getView()+'\nLibrary: '+self.library.getView()+'\nCoins: '+str(self.coins)+'\tActions: '+str(self.actions)+'\tBuys: '+str(self.buys)
	def setup(self, session, **kwargs):
		session.dp.send(signal='setup', player=self)
		self.session = session
		self.resolveEvent(Reshuffle)
		self.resolveEvent(DrawCards, amnt=5)
	def takeTurn(self, **kwargs):
		self.session.activePlayer = self
		self.session.turnFlag = kwargs.get('flag', '')
		self.resetValues()
		self.session.dp.send(signal='startTurn', player=self, flags=self.session.turnFlag)
		self.session.resolveTriggerQueue()
		self.actionPhase()
		self.treasurePhase()
		self.buyPhase()
		self.endTurn()
	def actionPhase(self, **kwargs):
		self.session.dp.send(signal='actionPhase', player=self)
		while True:
			self.session.resolveTriggerQueue()
			if self.actions<1 or not self.hand: break
			choice = self.user([o.view() for o in self.hand]+['EndActionPhase'], 'Choose action')
			if choice+1>len(self.hand): break
			if not 'ACTION' in self.hand[choice].types: continue
			self.actions-=1
			self.session.resolveEvent(CastCard, card=self.hand[choice], player=self)
			self.session.resolveTriggerQueue()
	def treasurePhase(self, **kwargs):
		self.session.dp.send(signal='treasurePhase', player=self)
		while True:
			if not self.hand: break
			self.session.resolveTriggerQueue()
			choice = self.user([o.view() for o in self.hand]+['PlayAllTreasures', 'EndTreasurePhase'], 'Choose treasure')
			if choice>len(self.hand): break
			if choice==len(self.hand):
				for card in copy.copy(self.hand):
					if not 'TREASURE' in card.types: continue
					self.session.resolveEvent(CastCard, card=card, player=self)
					self.session.resolveTriggerQueue()
				break
			elif 'TREASURE' in self.hand[choice].types:
				self.session.resolveEvent(CastCard, card=self.hand[choice], player=self)
				self.session.resolveTriggerQueue()
	def buyPhase(self, **kwargs):
		self.session.dp.send(signal='buyPhase', player=self)
		if self.debt>0: self.resolveEvent(PayDebt)
		self.session.resolveTriggerQueue()
		while self.buys>0:
			pileMap = {self.session.piles[n].getTopView(): n for n in self.session.piles}
			deventMap = {self.session.eventSupply[n].getTopView(): n for n in self.session.eventSupply}
			pileList = list(pileMap)
			deventList = list(deventMap)
			choice = self.user(pileList+deventList+['EndBuyPhase'], 'buySelection')
			if choice+1>len(pileList)+len(deventList): break
			elif choice<len(pileList): self.session.resolveEvent(PurchaseFromPile, frm=self.session.piles[pileMap[pileList[choice]]], player=self)
			else: self.resolveEvent(PurchaseDEvent, card=self.session.eventSupply[deventMap[deventList[choice-len(pileList)]]])
			self.session.resolveTriggerQueue()
		if self.debt>0: self.resolveEvent(PayDebt)
	def destroyAll(self, **kwargs):
		for card in copy.copy(self.inPlay): self.session.resolveEvent(Destroy, card=card, player=self)
	def discardHand(self, **kwargs):
		for card in copy.copy(self.hand): self.session.resolveEvent(Discard, card=card, player=self)
	def resetValues(self, **kwargs):
		self.coins = 0
		self.potions = 0
		self.actions = 1
		self.buys = 1
	def endTurn(self, **kwargs):
		self.session.dp.send(signal='endTurn', player=self)
		self.session.resolveTriggerQueue()
		self.discardHand()
		self.destroyAll()
		self.session.resolveEvent(DrawCards, amnt=self.eotdraw, player=self)
		self.eotdraw = 5
		self.session.resolveTriggerQueue()
		self.resetValues()
		self.session.dp.send(signal='turnEnded', player=self)
	def calcVP(self, **kwargs):
		cards = np.sum([o for o in [o.onGameEnd(self) for o in self.owns] if o])
		lands = np.sum([o for o in [self.session.landmarks[key].onGameEnd(self) for key in self.session.landmarks] if o])
		self.vp = int(self.victories+cards+lands)
	def endGame(self, **kwargs):
		self.discardHand()
		self.destroyAll()
		self.calcVP()
	def sessionEnd(self, **kwargs):
		self.session = None
	def selectCards(self, amnt=None, frm=None, optional=False, message='Choose cards', restriction=None, minimum=0, **kwargs):
		if frm==None: frm=self.hand
		options = [o for o in copy.copy(frm) if not(restriction and not restriction(o))]
		if not options: return []
		chosen = []
		def select():
			if not options: return True
			if optional and len(chosen)>=minimum:
				choice = self.user([o.view() for o in options]+['Done choosing'], message)
				if choice+1>len(options): return True
			else: choice = self.user([o.view() for o in options], message)
			chosen.append(options.pop(choice))
		if amnt!=None:
			for i in range(amnt):
				if select(): break
		else:
			while not select(): pass
		return chosen
	def selectCard(self, frm=None, optional=False, message='Choose card', restriction=None, **kwargs):
		if frm==None: frm=self.hand
		if not frm: return
		frm = [o for o in frm if not (restriction and not restriction(o))]
		if not frm: return
		if optional:
			choice = self.user([o.view() for o in frm]+['Done choosing'], message)
			if choice+1>len(frm): return
		else: choice = self.user([o.view() for o in frm], message)
		return frm[choice]
	def selectPile(self, optional=False, restriction=False, **kwargs):
		options = []
		for key in self.session.piles:
			if not (restriction and not restriction(self.session.piles[key].maskot)): options.append(key)
		if not options: return
		if optional:
			choice = self.user(options+['No pile'], 'Choose pile')
			if choice+1>len(options): return
		else: choice = self.user(options, 'Choose pile')
		return self.session.piles[options[choice]]
	def getPile(self, optional=False, restriction=None, **kwargs):
		options = []
		for key in self.session.piles:
			if self.session.piles[key].viewTop() and not (restriction and not restriction(self.session.piles[key].viewTop())): options.append(key)
		if not options: return
		if optional:
			choice = self.user(options+['No pile'], 'Choose pile')
			if choice+1>len(options): return
		else: choice = self.user(options, 'Choose pile')
		return self.session.piles[options[choice]]
	def pileCostingLess(self, coins=0, potions=0, debt=0, card=None, optional=False, restriction=None, **kwargs):
		if card:
			coins += card.coinPrice.access()
			potions += card.potionPrice.access()
			debt += card.debtPrice.access()
		options = []
		for key in self.session.piles:
			if self.session.piles[key].viewTop() and self.session.piles[key].viewTop().costLessThan(coins, potions, debt) and not (restriction and not restriction(self.session.piles[key].viewTop())): options.append(key)
		if not options: return
		if optional:
			choice = self.user(options+['No pile'], 'Choose pile')
			if choice+1>len(options): return
		else: choice = self.user(options, 'Choose pile')
		return self.session.piles[options[choice]]
	def pileCosting(self, coins=0, potions=0, debt=0, card=None, optional=False, restriction=None, **kwargs):
		if card:
			coins += card.coinPrice.access()
			potions += card.potionPrice.access()
			debt += card.debtPrice.access()
		options = []
		for key in self.session.piles:
			if self.session.piles[key].viewTop() and self.session.piles[key].viewTop().costEqualTo(coins, potions, debt) and not (restriction and not restriction(self.session.piles[key].viewTop())): options.append(key)
		if not options: return
		if optional:
			choice = self.user(options+['No pile'], 'Choose pile')
			if choice+1>len(options): return
		else: choice = self.user(options, 'Choose pile')
		return self.session.piles[options[choice]]
	def gainCostingLessThan(self, coin=0, potion=0, debt=0, card=None, optional=False, restriction=None, **kwargs):
		pile = self.pileCostingLess(coin, potion, debt, card, optional, restriction, **kwargs)
		if pile: self.resolveEvent(GainFromPile, frm=pile, **kwargs)
	def gainCosting(self, coin=0, potion=0, debt=0, card=None, optional=False, restriction=None, **kwargs):
		pile = self.pileCosting(coin, potion, debt, card, optional, restriction, **kwargs)
		if pile: self.resolveEvent(GainFromPile, frm=pile, **kwargs)
	def gain(self, optional=False, restriction=False, **kwargs):
		pile = self.getPile(optional, restriction, **kwargs)
		if pile: self.resolveEvent(GainFromPile, frm=pile, **kwargs)
	
class Token(object):
	name = 'baseToken'
	def __init__(self, session, **kwargs):
		self.owner = kwargs.get('owner', None)
		self.playerOwner = kwargs.get('playerOwner', None)
		self.session = session
		self.types = []
	def onAddPile(self, pile, **kwargs):
		pass
	def onLeavePile(self, pile, **kwargs):
		pass
	def jview(self, **kwargs):
		if self.playerOwner: n = self.playerOwner.name
		else: n = None
		return {'name': self.name, 'owner': n}
	def view(self, **kwargs):
		if self.playerOwner: return self.playerOwner.name+':'+self.name
		else: return self.name
	def connectCondition(self, tp, **kwargs):
		self.session.connectCondition(tp, **kwargs)
	
class Pile(CPile):
	def __init__(self, cardType, session, *args, **kwargs):
		super(Pile, self).__init__(*args, **kwargs)
		self.session = session
		self.cardType = cardType
		self.maskot = self.associateCard(cardType)
		self.maskot.disconnect()
		self.terminator = kwargs.get('terminator', False)
		self.maskot.onPileCreate(self, session)
		self.name = self.maskot.name
		self.tokens = CPile(name=self.name+' Tokens', owner=self)
	def gain(self, **kwargs):
		if not self: return
		return self.pop()
	def getView(self):
		top = self.viewTop()
		if not top: top = self.maskot
		ud = top.view()+' '+str(top.coinPrice.access())+'$'
		potions = top.potionPrice.access()
		debt = top.debtPrice.access()
		if potions: ud += str(potions)+'P'
		if debt: ud += str(debt)+'D'
		ud += ': '+str(len(self))
		if self.tokens: ud += ' ('+self.tokens.getFullView()+')'
		return ud
	def jview(self, **kwargs):
		top = self.viewTop()
		if top: return {'empty': False, 'card': top.jview(), 'tokens': self.tokens.jview(), 'length': len(self)}
		else: return {'empty': True, 'card': self.maskot.jview(), 'tokens': self.tokens.jview(), 'length': len(self)}
	def getTopView(self):
		top = self.viewTop()
		if top: return top.view()
		return self.maskot.view()
	def associateCard(self, tp, **kwargs):
		card = makeCard(self.session, tp, **kwargs)
		card.frmPile = self
		return card
	def addCard(self, tp, **kwargs):
		self.append(self.associateCard(tp, **kwargs))
	def addToken(self, token, session, **kwargs):
		session.dp.send(signal='addToken', pile=self, token=token)
		token.owner = self
		token.onAddPile(self)
		self.tokens.append(token)
	def getToken(self, token, session, **kwargs):
		i = self.tokens.index(token)
		if i==None: return
		self.removeToken(token, session, **kwargs)
		i = self.tokens.index(token)
		if i==None: return
		return self.tokens.pop(i)
	def removeToken(self, token, session, **kwargs):
		session.dp.send(signal='removeToken', pile=self, token=token)
		token.onLeavePile(self)
		token.owner = None
		
class Card(object):
	def __init__(self, obj=None, **kwargs):
		self.currentValues = obj
		self.printedValues = obj
		self.frmPile = None
		self.owner = None
	def setOwner(self, owner, **kwargs):
		self.owner = owner
	def setValues(self, values):
		self.currentValues = values
		self.printedValues = values
	def __getattr__(self, attr):
		if attr in self.__dict__: return getattr(self, attr)
		return getattr(self.currentValues, attr)
	
def makeCard(session, tp, **kwargs):
	c = Card()
	v = tp(session, card=c, **kwargs)
	c.setValues(v)
	return c
	
class BaseCard(WithPAs):
	ame = 'BaseCard'
	def __init__(self, session, **kwargs):
		self.card = kwargs.get('card', None)
		if not hasattr(self, 'types'): self.types = set()
		self.coinPrice = self.PA('coinPrice', kwargs.get('price', 0))
		self.potionPrice = self.PA('potionPrice', kwargs.get('potionPrice', 0))
		self.debtPrice = self.PA('potionPrice', kwargs.get('debtPrice', 0))
		#self.owner = None
		self.session = session
		self.connectedConditions = []
		self.name = kwargs.get('name', self.name)
	def onPileCreate(self, pile, session, **kwargs):
		for i in range(10): pile.addCard(type(self))
	def __getattr__(self, attr):
		if attr in self.__dict__: return getattr(self, attr)
		elif self.__dict__['card'] and attr in self.__dict__['card'].__dict__: return getattr(self.card, attr)
		else: raise AttributeError(attr)
	def onPlay(self, player, **kwargs):
		pass
	def onGameEnd(self, player, **kwargs):
		pass
	def disconnect(self, **kwargs):
		while self.connectedConditions: self.session.disconnectCondition(self.connectedConditions.pop())
	def view(self, **kwargs):
		return self.name
	def jviewAdd(self, **kwargs):
		return {}
	def jview(self, **kwargs):
		d = {'name': self.view(), 'types': list(self.types), 'c': self.coinPrice.access(), 'p': self.potionPrice.access(), 'd': self.debtPrice.access()}
		d.update(self.jviewAdd(**kwargs))
		return d
	def connectCondition(self, tp, **kwargs):
		self.connectedConditions.append(self.session.connectCondition(tp, **kwargs))
	def costLessThan(self, coins=0, potions=0, debt=0, card=None, **kwargs):
		if card:
			coins = card.coinPrice.access()
			potions = card.potionPrice.access()
			debt = card.debtPrice.access()
		works = False
		if self.coinPrice.access()>coins: return False
		elif self.coinPrice.access()<coins: works = True
		if self.potionPrice.access()>potions: return False
		elif self.potionPrice.access()<potions: works = True
		if self.debtPrice.access()>debt: return False
		elif self.debtPrice.access()<debt: works = True
		return works
	def costEqualTo(self, coins=0, potions=0, debt=0, card=None, **kwargs):
		if card:
			coins = card.coinPrice.access()
			potions = card.potionPrice.access()
			debt = card.debtPrice.access()
		return self.coinPrice.access()==coins and self.potionPrice.access()==potions and self.debtPrice.access()==debt
	
class DEvent(WithPAs):
	name = 'BaseDEvent'
	def __init__(self, session, **kwargs):
		self.coinPrice = self.PA('coinPrice', kwargs.get('price', 0))
		self.potionPrice = self.PA('potionPrice', kwargs.get('potionPrice', 0))
		self.debtPrice = self.PA('potionPrice', kwargs.get('debtPrice', 0))
		self.tokens = CPile(name='tokens')
		self.session = session
		self.owner = None
	def view(self, **kwargs):
		ud = self.name+' '+str(self.coinPrice.access())+'$'
		potions = self.potionPrice.access()
		debt = self.debtPrice.access()
		if potions: ud += str(potions)+'P'
		if debt: ud += str(debt)+'D'
		return ud
	def jview(self, **kwargs):
		return {'c': self.coinPrice.access(), 'p': self.potionPrice.access(), 'd': self.debtPrice.access(), 'tokens': self.tokens}
	def getTopView(self, **kwargs):
		return self.name
	def onBuy(self, player, **kwargs):
		pass
	def checkBefore(self, player, **kwargs):
		for i in range(len(player.session.events)-1, -1, -1):
			if player.session.events[i][0]=='BuyDEvent' and player.session.events[i][1]['card'].name==self.name: return False
			elif player.session.events[i][0]=='startTurn': break
		return True
	def connectCondition(self, tp, **kwargs):
		self.session.connectCondition(tp, **kwargs)

class Landmark(WithPAs):
	name = 'BaseLandmark'
	def __init__(self, session, **kwargs):
		self.session = session
		self.tokens = CPile(name='tokens')
		self.owner = None
		self.points = None
	def view(self, **kwargs):
		if self.tokens: return self.name+'('+self.tokens.getView()+')'
		else: return self.name
	def jview(self, **kwargs):
		return {'tokens': self.tokens.jview(), 'points': self.points}
	def onGameEnd(self, player, **kwargs):
		pass
	
class Treasure(BaseCard):
	def __init__(self, session, **kwargs):
		super(Treasure, self).__init__(session, **kwargs)
		self.coinValue = self.PA('coinValue', 0)
		self.potionValue = self.PA('potionValue', 0)
		self.types.add('TREASURE')
	def onPlay(self, player, **kwargs):
		super(Treasure, self).onPlay(player, **kwargs)
		player.session.resolveEvent(AddCoin, player=player, amnt=self.coinValue.access())
		player.session.resolveEvent(AddPotion, player=player, amnt=self.potionValue.access())
		
class Victory(BaseCard):
	def __init__(self, session, **kwargs):
		super(Victory, self).__init__(session, **kwargs)
		self.victoryValue = self.PA('victoryValue', 0)
		self.types.add('VICTORY')
	def onGameEnd(self, player, **kwargs):
		return self.victoryValue.access()
	def onPileCreate(self, pile, session, **kwargs):
		if len(session.players)>2: amnt = 12
		else: amnt = 8
		for i in range(amnt): pile.addCard(type(self))
		
class Action(BaseCard):
	def __init__(self, session, **kwargs):
		super(Action, self).__init__(session, **kwargs)
		self.types.add('ACTION')
		
class Cursed(BaseCard):
	def __init__(self, session, **kwargs):
		super(Cursed, self).__init__(session, **kwargs)
		self.victoryValue = self.PA('victoryValue', -1)
		self.types.add('CURSED')
	def onGameEnd(self, player, **kwargs):
		return self.victoryValue.access()
		
class Reaction(object):
	def __init__(self, session, **kwargs):
		if not hasattr(self, 'types'): self.types = set()
		self.types.add('REACTION')
		
class Attack(object):
	def __init__(self, session, **kwargs):
		if not hasattr(self, 'types'): self.types = set()
		self.types.add('ATTACK')
	def attackOpponents(self, player, **kwargs):
		results = []
		for aplayer in player.session.getPlayers(player):
			if aplayer!=player: results.append(player.resolveEvent(ResolveAttack, source=self.card, attack=self.attack, victim=aplayer, **kwargs))
		return results
	def attackAll(self, player, **kwargs):
		results = []
		for aplayer in player.session.getPlayers(player): results.append(player.resolveEvent(ResolveAttack, source=self.card, attack=self.attack, victim=aplayer, **kwargs))
		return results
	def attack(self, player, **kwargs):
		pass
			
class Duration(object):
	class DurationTrigger(DelayedTrigger):
		name = 'DurationTrigger'
		defaultTrigger = 'startTurn'
		def condition(self, **kwargs):
			return kwargs['player']==self.source.owner
		def resolve(self, **kwargs):
			self.source.owner.resolveEvent(ResolveDuration, card=self.source)	
	def __init__(self, session, **kwargs):
		if not hasattr(self, 'types'): self.types = []
		self.types.add('DURATION')
		self.connectCondition(Replacement, trigger='Destroy', source=self, resolve=self.resolveDestroy, condition=self.conditionDestroy)
	def onPlay(self, player, **kwargs):
		self.session.connectCondition(self.DurationTrigger, source=self)
	def conditionDestroy(self, **kwargs):
		if not kwargs['card']==self.card: return False
		for i in range(len(self.session.events)-1, -1, -1):
			if self.session.events[i][0]=='PlayCard' and self.session.events[i][1]['card']==self.card: return True
			elif self.session.events[i][0]=='startTurn': return False
	def resolveDestroy(self, event, **kwargs):
		return
	def duration(self, **kwargs):
		pass
			
class Reserve(object):
	triggerSignal = ''
	def __init__(self, session, **kwargs):
		self.types.add('RESERVE')
		self.connectCondition(Trigger, trigger=self.triggerSignal, source=self, resolve=self.resolveCall, condition=self.conditionCall)
	def onPlay(self, player, **kwargs):
		player.resolveEvent(MoveCard, frm=player.inPlay, to=player.mats['Tavern'], card=self.card)
	def callRestriction(self, **kwargs):
		return kwargs['player']==self.owner
	def conditionCall(self, **kwargs):
		return self.owner and self.card in self.owner.mats['Tavern'] and self.callRestriction(**kwargs)
	def resolveCall(self, **kwargs):
		if self.owner.user(('yes', 'no'), 'Call '+self.view()): return
		self.owner.resolveEvent(MoveCard, frm=self.owner.mats['Tavern'], to=self.owner.inPlay, card=self.card)
		self.call(**kwargs)
	def call(self, **kwargs):
		pass
	def onPileCreate(self, pile, session, **kwargs):
		session.addMat('Tavern')

class Traveler(object):
	def __init__(self, session, **kwargs):
		self.types.add('TRAVELER')
		self.morph = None
		self.connectCondition(Trigger, trigger='endTurn', source=self.card, resolve=self.resolveEndTurn, condition=self.conditionEndTurn)
	def conditionEndTurn(self, **kwargs):
		return self.owner and kwargs['player']==self.owner and self.card in self.owner.inPlay
	def resolveEndTurn(self, **kwargs):
		if not self.owner.user(('no', 'yes'), 'Upgrade '+self.view()): return
		owner = self.owner
		owner.resolveEvent(PutBackCard, frm=owner.inPlay, card=self.card)
		owner.resolveEvent(TakeFromPile, frm=self.session.NSPiles[self.morph.name])
	def onPileCreate(self, pile, session, **kwargs):
		session.require(self.morph)
	
class Gathering(object):
	def __init__(self, session, **kwargs):
		if not hasattr(self, 'types'): self.types = set()
		self.types.add('GATHERING')
	
if __name__=='__main__':
	random.seed()