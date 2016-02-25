import socket
import threading		
import struct
import pickle
import re

s = None

def gN(ob):
	if hasattr(ob, 'playerName'): return ob.playerName
	elif hasattr(ob, 'name'): return ob.name
	else: return str(ob)

def testUser(options, name='noName'):
	if not name=='buySelection':
		print(name, end=': ')
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

class traa(threading.Thread):
	def __init__(self, f, **kwargs):
		threading.Thread.__init__(self)
		self.f = f
		self.vals = kwargs
	def run(self):
		self.f(**self.vals)

def request(head):
	s.send(('requ'+head).encode('UTF-8'))
		
def updt(signal, **kwargs):
	if signal=='startTurn':
		print('-'*36)
	elif signal=='beginRound':
		print('*'*36)
	#elif signal=='actionPhase':
	#	request('stat')
	#elif signal=='buyPhase':
	#	request('king')
	#	request('stat')
	print('>'+signal, end='::'+' '*(18-len(signal)))
	for key in kwargs:
		if key=='sender': continue
		print(key+': '+str(kwargs[key]), end=', ')
	print('')
	
def answer(**kwargs):
	s.send('answ'.encode('UTF-8')+struct.pack('I', testUser(kwargs['options'], kwargs['name'])))
	
def lyt(**kwargs):
	while True:
		try:
			head = s.recv(4).decode('UTF-8')
			if head=='ques':
				length = struct.unpack('I', s.recv(4))[0]
				recieved = s.recv(length)
				if not len(recieved)==length:
					print('lost package')
					continue
				upickle = pickle.loads(recieved)
				aF = traa(answer, name=upickle[0], options=upickle[1])
				aF.start()
			elif head=='updt':
				length = struct.unpack('I', s.recv(4))[0]
				recieved = s.recv(length)
				if not len(recieved)==length:
					print('lost package')
					continue
				l = pickle.loads(recieved)
				updt(l[0], **l[1])
			elif head=='resp':
				length = struct.unpack('I', s.recv(4))[0]
				print(s.recv(length).decode('UTF-8'))
		except: pass
		
def tilServer(**kwargs):
	toServer = input(': ')
	s.send(toServer.encode('UTF-8'))
		
def main():
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	l = traa(lyt)
	l.start()
	ts = traa(tilServer)
	ts.start()

if __name__=='__main__':
	HOST = str(socket.gethostbyname(socket.gethostname()))
	print(HOST)
	PORT = 6700
	main()