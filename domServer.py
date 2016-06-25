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
	def juse(self, options, name='noName'):
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
		#self.deventPM = probMap((0.1, 0.5, 0.4))
		#self.landmarkPM = probMap((0.1, 0.5, 0.4))
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
	def makeGame(self, allCards=False, printEvents=False, kingdom='', **kwargs):
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
		#options = baseSet+prosperity+seaside+adventures+alchemy+hinterlands+empires
		options = baseSet+seaside+darkages+adventures+alchemy+empires+prosperity
		allDEvents = adventuresDEvents+promoDEvents+empiresDEvents
		landmarks = empiresLandmarks
		if allCards:
			game.makePiles(baseSetBase)
			options += testCards
			game.makePiles(options)
			game.makeDEvents(allDEvents)
			game.makeLandmarks(landmarks)
		else:
			makeGame(game, baseSetBase, cardSetsD, deventSetsD, landSetsD, kingdom)
		if printEvents: game.dp.connect(self.evLogger)
		game.makeStartDeck()
		gT = traa(game.start)
		gT.start()
	def recvPack(self):
		head = self.recvLen().decode('UTF-8')
		l = struct.unpack('I', self.recvLen())[0]
		if l: body = json.loads(self.recvLen(l).decode('UTF-8'))
		else: body = {}
		return head, body
	def run(self):
		while self.running:
			head, body = self.recvPack()
			if head==b'':
				print('recived empty string')
				self.kill()
				break
			self.command(head, body)
	def command(self, head, body):
		if head=='GAME': self.makeGame(kingdom=body['kingdom'])
		elif head=='TEST': self.makeGame(True)
		elif head=='DEBU': self.makeGame(True, True)
		elif head=='RECO':
			print(self.oaddr, playerConnections)
			if not self.oaddr in list(playerConnections): return
			self.linkPlayer(playerConnections[self.oaddr])
			if self.player.payload: self.sendJson('QUES', self.player.payload)
		elif head=='CONC': self.player.game.concede(self.player)
		elif head=='NAME' and 'name' in body: self.playerName = body['name']
		elif head=='ANSW' and self.player: self.player.answerF(body['index'])
		elif head=='RUPD' and self.player: self.sendJson('UPDT', self.player.jsonUI())
		elif head=='RQUE' and self.player: self.sendJson('QUES', self.player.payload)
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
	cardSetsD = {key: {o.name: o for o in cardSets[key]} for key in cardSets}
	deventSetsD = {key: {o.name: o for o in deventSets[key]} for key in deventSets}
	landSetsD = {key: {o.name: o for o in landmarkSets[key]} for key in landmarkSets}
	