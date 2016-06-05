import sys
import server
from cards import *
from devents import *
from landmarks import *
import pickle
import threading
import struct
import socket

class traa(threading.Thread):
	def __init__(self, f, **kwargs):
		threading.Thread.__init__(self)
		self.f = f
		self.vals = kwargs
	def run(self):
		self.f(**self.vals)
	
playerConnections = {}
games = []
	
class PPlayer(Player):
	def __init__(self, **kwargs):
		super(PPlayer, self).__init__(**kwargs)
		self.oplayer = None
		self.useLock = threading.Semaphore()
		self.useLock.acquire()
		self.user = self.use
		self.payload = None
		self.answer = None
		self.userAddress = None
	def use(self, options, name='noName'):
		for player in self.game.players: player.updateUI()
		if len(options)==1 or not self.game.running: return 0
		self.payload = pickle.dumps((name, options))
		self.oplayer.sendPayload('ques', self.payload)
		self.useLock.acquire()
		self.payload = None
		if type(self.answer)==int and self.answer in range(len(options)): return self.answer
		else: return len(options)-1
	def answerF(self, answer):
		self.answer = answer
		self.useLock.release()
	def gameEnd(self, **kwargs):
		super(PPlayer, self).gameEnd(**kwargs)
		del playerConnections[self.oplayer.oaddr]
		self.oplayer.player = None
		self.answer = None
		self.useLock.release()
			
class OnlinePlayer(server.CST):
	def __init__(self, **kwargs):
		super(OnlinePlayer, self).__init__(**kwargs)
		server.CST.__init__(self, **kwargs)
		self.playerName = 'p'+str(server.idcnt)
		self.defaultRecvLen = 4
		self.player = None
		self.indents = []
	def linkPlayer(self, player):
		self.player = player
		player.oplayer = self
		player.userAdress = self.addr
		player.name = self.playerName
		player.channelOut = self.channelOutFunc
		player.uiupdate = self.uiupFunc
	def uiupFunc(self, z, sz, c):
		sc = c.encode('UTF-8')
		self.send(('uiup'+z+sz).encode('UTF-8')+struct.pack('I', len(sc))+sc)
	def channelOutFunc(self, l, head='updt', picklel=True):
		if picklel:	payload = pickle.dumps(l)
		else: payload = l.encode('UTF-8')
		self.send(head.encode('UTF-8')+struct.pack('I', len(payload))+payload)
	def sendPayload(self, head, payload):
		self.send(head.encode('UTF-8')+struct.pack('I', len(payload))+payload)
	def evLogger(self, signal, **kwargs):
		if len(signal)>16 and signal[:16]=='AccessAttribute_': return
		if signal[-6:]=='_begin': self.indents.append(signal[:-6])
		elif signal in self.indents: self.indents.remove(signal)
		print('>'+'|\t'*len(self.indents)+signal+':: '+str(list(kwargs)))
	def makeGame(self, allCards=False, printEvents=False, **kwargs):
		players = []
		for key in server.csts:
			if server.csts[key].player==None:
				player = PPlayer()
				server.csts[key].linkPlayer(player)
				playerConnections[server.csts[key].oaddr] = player
				players.append(player)
		if not players: return
		game = Game(players=players)
		games.append(game)
		for player in game.players:	player.game = game
		game.makePiles(baseSetBase)
		#options = baseSet+prosperity+seaside+adventures+alchemy+hinterlands+empires
		options = baseSet+seaside+darkages+adventures+alchemy+empires+prosperity
		allDEvents = adventuresDEvents+promoDEvents+empiresDEvents
		landmarks = empiresLandmarks
		if allCards:
			options += testCards
			game.makePiles(options)
			game.makeDEvents(allDEvents)
			game.makeLandmarks(landmarks)
		else:
			game.makeDEvents(random.sample(allDEvents, random.randint(0, 2)))
			game.makeLandmarks(random.sample(landmarks, random.randint(0, 2)))
			#piles = random.sample(empires, 2)
			piles = random.sample(options, 10)
			game.makePiles(piles)
		if printEvents: game.dp.connect(self.evLogger)
		game.makeStartDeck()
		gT = traa(game.start)
		gT.start()
	def command(self, ind):
		print(ind)
		if not len(ind)==4: return
		try: streng = ind.decode('UTF-8')
		except: streng = None
		if streng=='game':
			self.makeGame()
		elif streng=='test':
			self.makeGame(True)
		elif streng=='debu':
			self.makeGame(True, True)
		elif streng=='requ':
			self.channelOutFunc(self.request(self.recvLen(4).decode('UTF-8')), 'resp', False)
		elif streng=='reco':
			print(self.oaddr, playerConnections)
			if not self.oaddr in list(playerConnections): return
			self.linkPlayer(playerConnections[self.oaddr])
			if self.player.payload: self.sendPayload('ques', self.player.payload)
		elif streng=='conc':
			self.player.game.concede(self.player)
		elif self.player: 
			self.player.answerF(struct.unpack('I', ind)[0])
	def use(self, options, name='noName'):
		payload = pickle.dumps((name, options))
		self.send('ques'.encode('UTF-8')+struct.pack('I', len(payload))+payload)
		print('send')
		self.useLock.acquire()
		if self.answer in range(len(options)): return self.answer
		else: return len(options)-1
	
if __name__=='__main__':
	random.seed()
	HOST = str(socket.gethostbyname(socket.gethostname()))
	PORT = 6700
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', PORT))
	print(HOST+' rec at '+str(PORT))
	s.listen(1)
	ct = server.clientThread(s, OnlinePlayer)
	ct.start()
	print('ct started')
	