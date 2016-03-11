import sys
import server
from cards import *
from events import *
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
		self.payload = pickle.dumps((name, options))
		self.oplayer.sendPayload('ques', self.payload)
		self.useLock.acquire()
		self.payload = None
		if self.answer in range(len(options)): return self.answer
		else: return len(options)-1
	def answerF(self, answer):
		self.answer = answer
		self.useLock.release()
			
class OnlinePlayer(server.CST):
	def __init__(self, **kwargs):
		super(OnlinePlayer, self).__init__(**kwargs)
		server.CST.__init__(self, **kwargs)
		self.playerName = 'p'+str(server.idcnt)
		self.defaultRecvLen = 4
		self.player = None
	def linkPlayer(self, player):
		self.player = player
		player.oplayer = self
		player.userAdress = self.addr
		player.name = self.playerName
		player.channelOut = self.channelOutFunc
	def channelOutFunc(self, l, head='updt', picklel=True):
		if picklel:	payload = pickle.dumps(l)
		else: payload = l.encode('UTF-8')
		self.send(head.encode('UTF-8')+struct.pack('I', len(payload))+payload)
	def sendPayload(self, head, payload):
		self.send(head.encode('UTF-8')+struct.pack('I', len(payload))+payload)
	def command(self, ind):
		print(ind)
		if not len(ind)==4: return
		if ind.decode('UTF-8')=='answ':
			self.player.answerF(struct.unpack('I', self.recv(4))[0])
		elif ind.decode('UTF-8')=='game':
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
			#game = Game(players=[server.csts[key] for key in server.csts])
			for player in game.players:	player.game = game
			game.makePiles(baseSetBase)
			options = baseSet+prosperity+seaside+adventures
			allEvents = adventuresEvents
			#game.makePiles(options)
			#game.makeEvents(allEvents)
			game.makeEvents(random.sample(allEvents, random.randint(0, 2)))
		#game.makePiles(random.sample(options, 10))
			game.makeStartDeck()
			gT = traa(game.start)
			gT.start()
		elif ind.decode('UTF-8')=='requ':
			self.channelOutFunc(self.request(self.recv(4).decode('UTF-8')), 'resp', False)
		elif ind.decode('UTF-8')=='reco':
			print(self.oaddr, playerConnections)
			if not self.oaddr in list(playerConnections): return
			self.linkPlayer(playerConnections[self.oaddr])
			if self.player.payload: self.sendPayload('ques', self.player.payload)
	def use(self, options, name='noName'):
		payload = pickle.dumps((name, options))
		self.send('ques'.encode('UTF-8')+struct.pack('I', len(payload))+payload)
		print('send')
		self.useLock.acquire()
		if self.answer in range(len(options)): return self.answer
		else: return len(options)-1
	
if __name__=='__main__':
	#dp.connect(tdominion.logFunc)
	#makePiles(baseSet)
	#makePiles(prosperity)
	#makePiles(platColony)
	#makePiles(seaside)
	HOST = str(socket.gethostbyname(socket.gethostname()))
	print(HOST)
	PORT = 6700
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', PORT))
	print("rec at "+str(PORT))
	s.listen(1)
	ct = server.clientThread(s, OnlinePlayer)
	ct.start()
	print('ct started')
	