import sys
import server
from cards import *
from devents import *
from landmarks import *
import pickle
import threading
import struct
import socket
import json

class probMap(list):
	def get(self, val):
		sum = 0
		for i in range(len(self)):
			sum += self[i]
			if val<=sum: return i
		return len(self)-1

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
		self.user = self.juse
		self.payload = None
		self.answer = None
		self.userAddress = None
	def oldUse(self, options, name='noName'):
		print(self.jsonUI())
		for player in self.game.players: player.updateUI()
		if len(options)==1 or not self.game.running: return 0
		self.payload = pickle.dumps((name, options))
		self.oplayer.sendPayload('ques', self.payload)
		self.useLock.acquire()
		self.payload = None
		if type(self.answer)==int and self.answer in range(len(options)): return self.answer
		else: return len(options)-1
	def juse(self, options, name='noName'):
		print(self.jsonUI())
		for player in self.game.players: player.oplayer.sendJson('UPDT', player.jsonUI())
		if len(options)==1 or not self.game.running: return 0
		self.payload = {'name': name, 'options': options}
		self.oplayer.sendJson('QUES', self.payload)
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
		self.deventPM = probMap((0.1, 0.5, 0.4))
		self.landmarkPM = probMap((0.1, 0.5, 0.4))
	def linkPlayer(self, player):
		self.player = player
		player.oplayer = self
		player.userAdress = self.addr
		player.name = self.playerName
		player.channelOut = self.jchannelOut
		player.uiupdate = self.uiupFunc
	def uiupFunc(self, z, sz, c):
		sc = c.encode('UTF-8')
		self.send(('uiup'+z+sz).encode('UTF-8')+struct.pack('I', len(sc))+sc)
	def jchannelOut(self, name, **kwargs):
		kwargs.update({'name': name})
		self.sendJson('NLOG', kwargs)
	def channelOutFunc(self, l, head='updt', picklel=True):
		if picklel:	payload = pickle.dumps(l)
		else: payload = l.encode('UTF-8')
		self.send(head.encode('UTF-8')+struct.pack('I', len(payload))+payload)
	def sendJson(self, head, content=None):
		print(content)
		h = head.encode('UTF-8')
		assert (len(h)==4), 'Wrong head length'
		if content: s = json.dumps(content).encode('UTF-8')
		else: s = ''
		i = struct.pack('I', len(s))
		self.send(h+i+s)
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
			game.makeDEvents(random.sample(allDEvents, self.deventPM.get(random.random())))
			game.makeLandmarks(random.sample(landmarks, self.landmarkPM.get(random.random())))
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
		elif streng=='name':
			l = self.recvLen()
			ll = struct.unpack('I', l)[0]
			n = self.recvLen(ll)
			nn = n.decode('UTF-8')
			self.playerName = nn
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
	