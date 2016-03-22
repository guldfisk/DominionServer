import threading
import socket
import time
import struct

class traa(threading.Thread):
	def __init__(self, func):
		threading.Thread.__init__(self)
		self.func = func
	def run(self):
		self.func()
		
csts = {}
		
def clean():
	forDelete = []
	for key in csts:
		if not csts[key].running:
			forDelete.append(key)
	for key in forDelete:
		del csts[key]
		
		
class CST(threading.Thread):
	def __init__(self, **kwargs):
		threading.Thread.__init__(self)
		self.conn = kwargs['conn']
		self.addr = kwargs['addr']
		self.oaddr = kwargs['oaddr']
		self.defaultRecvLen = kwargs.get('drl', 8192)
		self.running = True
		self.parent = kwargs.get('parent', None)
	def run(self):
		while self.running:
			data = self.recvLen()
			if data==b'':
				print('recived empty string')
				self.kill()
				break
			self.command(data)
	def command(self, ind):
		pass
	def recv(self, l=None):
		if not l: ll = self.defaultRecvLen
		else: ll = l
		try: data = self.conn.recv(ll)
		except:
			print('error: conn.recv')
			data = b''
		return(data)
	def recvLen(self, l=4):
		bytes = b''
		while len(bytes)<l: bytes += self.conn.recv(1)
		return bytes
	def recvStr(self):
		data = self.recv()
		try:
			streng = data.decode('utf-8')
		except:
			streng = 'NOT DECODABLE'
		if streng == '<empty>':
			streng = ''
		return(streng)
	def sendStr(self, ind):
		try:
			self.conn.sendall(ind.encode('utf-8'))
		except:
			self.kill()
	def send(self, ind):
		try:
			self.conn.sendall(ind)
		except:
			self.kill()
	def kill(self):
		print('killing '+self.addr)
		self.conn.close()
		self.running = False
		clean()

class SCST(CST):
	def __init__(self, **kwargs):
		super(SCST, self).__init__(**kwargs)
		self.waiting = {}
		self.cnt = 0
	def run(self):
		while self.running:
			data = self.recv()
			if data==b'':
				print('recived empty string')
				self.kill()
			elif data.decode('UTF-8')=='conf':
				n = self.recv(4)
				if not len(n)==4: continue
				nn = struct.pack('I', n)[0]
				if not nn in list(self.waiting): continue
				self.waiting[nn].release()
				del self.waiting[nn]
			else: self.command(data)
	def send(self, ind):
		self.conn.sendall(ind)
			
class HBCT(CST):
	def __init__(self, **kwargs):
		super(HBCT, self).__init__(**kwargs)
		self.beatSource = kwargs.get('beatSource', None)
		self.beatInterval = kwargs.get('beatInterval', 10)
		self.ori_time = time.time()
		self.next_call = time.time()
		self.beating = True
		self.ntick = 0
	def startBeat(self):
		while self.beating:
			print('BEATING')
			if self.ori_time-self.next_call+self.beatInterval>0:
				time.sleep(self.ori_time-self.next_call+self.beatInterval)
			if self.beatSource:
				self.send(self.beatSource(self.ntick))	
			self.ntick += 1
			self.next_call = time.time()
	def run(self):
		bt = traa(self.startBeat)
		bt.start()
		super(HBCT, self).run()
	
def sendToAll(ind):
	for key in csts:
		csts[key].send(ind)
			
def checkAll():
	for key in csts:
		if not (csts[key].isAlive() and csts[key].running):
			print('Del '+key)
			del csts[self.addr]
			
def killAll():
	print('killing all')
	global ct
	for key in csts:
		csts[key].running = False
	ct.running = False
idcnt = 0		
class clientThread(threading.Thread):
	def __init__(self, socket=None, CST=CST):
		threading.Thread.__init__(self)
		self.s = socket
		self.running = True
		self.spawn = CST
	def clean(self):
		pass
	def kill(self):
		self.s.close()
		self.running = False
	def run(self):
		global idcnt
		while self.running:
			conn, addr = self.s.accept()
			idcnt += 1
			adr = addr[0]+'::'+str(idcnt)
			csts[adr] = self.spawn(conn=conn, addr=adr, oaddr=addr[0])
			csts[adr].daemon = True
			csts[adr].start()
			print(csts)

ct = clientThread()

def rec(bindArg=''):
	global inds
	global ct
	HOST = str(socket.gethostbyname(socket.gethostname()))
	print(HOST)
	PORT = 6700
	for i in range(1):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((bindArg, PORT))
		print("rec at "+str(PORT))
		s.listen(1)
		ct = clientThread(s)
		print('hue')
		ct.start()
		print('ct started')
	while True:
		ind = input(str(csts)+': ')
		if ind=='exit':
			ct.kill()
			#while True:
			#	print(ct)
			break
		data = input(str(csts)+'what: ')
		csts[ind].send(data.encode('ascii'))

if __name__=='__main__':
	rec()