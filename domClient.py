import socket
import threading		
import struct
import pickle
import re
import wave
import pyaudio

s = None

def readWav(name):
	wf = wave.open(name, 'rb')
	return wf.readframes(wf.getnframes())

notification = readWav('Resources\\Bass_drum_2.wav')
	
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

def play(**kwargs):  
	p = pyaudio.PyAudio() 
	mfrate = 44100
	stream = p.open(format = 8, channels = 1, rate = mfrate, output = True)
	stream.write(kwargs['sound'])
	stream.stop_stream()  
	stream.close()  
	p.terminate()
		
def playSound(sound):
	pt = traa(play, sound=sound)
	pt.start()
		
def request(head):
	s.send(('requ'+head).encode('UTF-8'))
		
me = None
		
def updt(signal, **kwargs):
	global me
	if signal=='startTurn':
		print('-'*36)
		if kwargs['player']==me: playSound(notification)
	if signal=='globalSetup':
		if 'you' in kwargs: me = kwargs['you']
	elif signal=='beginRound':
		print('*'*36)
	print('>'+signal, end='::'+' '*(18-len(signal)))
	for key in kwargs:
		if key=='sender': continue
		print(key+': '+str(kwargs[key]), end=', ')
	print('')
	
def answer(**kwargs):
	s.send('answ'.encode('UTF-8')+struct.pack('I', testUser(kwargs['options'], kwargs['name'])))
	
def lyt(**kwargs):
	while True:

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
			recieved = s.recv(4)
			if not len(recieved)==4:
				print('lost package')
				continue
			length = struct.unpack('I', recieved)[0]
			print(s.recv(length).decode('UTF-8'))

		
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
	HOST = input('connect to: ')
	if HOST=='': HOST = 'localhost'
	#HOST = 'localhost'
	#HOST = str(socket.gethostbyname(socket.gethostname()))
	print(HOST)
	PORT = 6700
	main()