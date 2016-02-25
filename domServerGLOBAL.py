import sys
sys.path.append('C:\\Projeter\\farligfarligslange\\mtgjson\\fraoliserver')
import server
from cards import *
import pickle
import threading
import struct
import socket
import tdominion
	
class traa(threading.Thread):
	def __init__(self, f, **kwargs):
		threading.Thread.__init__(self)
		self.f = f
		self.vals = kwargs
	def run(self):
		self.f(**self.vals)
	
class OnlinePlayer(Player, server.CST):
	def __init__(self, **kwargs):
		super(OnlinePlayer, self).__init__(**kwargs)
		server.CST.__init__(self, **kwargs)
		self.playerName = 'p'+str(server.idcnt)
		self.defaultRecvLen = 4
		self.user = self.use
		self.answer = None
		self.channelOut = self.channelOutFunc
		self.useLock = threading.Semaphore()
		self.useLock.acquire()
	def channelOutFunc(self, l, head='updt', picklel=True):
		if picklel:	payload = pickle.dumps(l)
		else: payload = l.encode('UTF-8')
		self.send(head.encode('UTF-8')+struct.pack('I', len(payload))+payload)
	def command(self, ind):
		print(ind)
		if not len(ind)==4: return
		if ind.decode('UTF-8')=='answ':
			self.answer = struct.unpack('I', self.recv(4))[0]
			self.useLock.release()
		elif ind.decode('UTF-8')=='game':
			makePiles(baseSetBase)
			options = baseSet+prosperity+seaside
			makePiles(random.sample(options, 10))
			#makePiles(options)
			makeStartDeck()
			gT = traa(game)
			gT.start()
		elif ind.decode('UTF-8')=='requ':
			self.channelOutFunc(self.request(self.recv(4).decode('UTF-8')), 'resp', False)
	def use(self, options, name='noName'):
		payload = pickle.dumps((name, options))
		self.send('ques'.encode('UTF-8')+struct.pack('I', len(payload))+payload)
		print('send')
		self.useLock.acquire()
		if self.answer in range(len(options)): return self.answer
		else: return len(options)-1
	
if __name__=='__main__':
	dp.connect(tdominion.logFunc)
	#makePiles(baseSet)
	#makePiles(prosperity)
	#makePiles(platColony)
	#makePiles(seaside)
	print(list(piles))
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
	