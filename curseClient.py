import curses
import time
import threading
import curses.textpad
import sys
import math
import socket
import threading		
import struct
import pickle
import re

s = None
PORT = 6700
HOST = 'localhost'

def gN(ob):
	if hasattr(ob, 'playerName'): return ob.playerName
	elif hasattr(ob, 'name'): return ob.name
	else: return str(ob)

class InputBuffer(object):
	def __init__(self):
		self.lock = threading.Semaphore()
		self.lock.acquire()
		self.value = []
	def get(self):
		while not self.value: self.lock.acquire()
		return self.value.pop()
	def add(self, value):
		self.value = [value]
		self.lock.release()
	
ipbuf = InputBuffer()
	
def testUser(options, name='noName'):
	if not name=='buySelection':
		logw.addstr(name, end=': ')
		for option in options: logw.addstr(gN(option), end=', ')
	choicePosition = -2
	while choicePosition<-1:
		choice = ipbuf.get()
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

def log(ssstr, *strs, **kwargs):
	file = open('log.txt', 'a')
	file.write(str(ssstr))
	for sstr in strs:
		file.write(', '+str(sstr))
	file.write(kwargs.get('end', '\n'))
	file.close()
		
class ScrollWithInput(object):
	def __init__(self, **kwargs):
		self.windowX = kwargs.get('windowX', 0); self.windowY = kwargs.get('windowY', 0)
		self.height = kwargs.get('height', 10); self.width = kwargs.get('width', 10)
		self.scrollDepth = kwargs.get('scrollDepth', 100)
		self.log = curses.newpad(self.scrollDepth, self.width)
		self.log.move(self.scrollDepth-1, 0)
		self.iw = curses.newwin(1, self.width, self.windowY+self.height+1, self.windowX)
		self.textbox = curses.textpad.Textbox(self.iw)
		self.log.keypad(True)
		self.log.scrollok(True)
		self.pos = self.scrollDepth-self.height-1
		self.iput = ''
		self.running = True
	def validation(self, c):
		if c==ord('q'): sys.exit()
		elif c==curses.KEY_UP:
			if not self.pos<1: self.pos -= 1
			self.refresh()
			log(self.pos)
		elif c==curses.KEY_DOWN:
			if not self.pos>self.scrollDepth-self.height-2: self.pos += 1
			self.refresh()
		elif c==curses.KEY_RIGHT:
			self.running = False
			return 10
		return c
	def command(self, string):
		pass
	def run(self):
		self.running = True
		while self.running:
			s = self.textbox.edit(self.validation)
			self.command(s[:-1])
			self.iw.clear()
			#self.log.addstr(self.scrollDepth-1, 0, s+'\n')
			self.addstr(s)
			self.refresh()
	def refresh(self):
		self.log.refresh(self.pos, 0, self.windowY, self.windowX, self.windowY+self.height, self.windowX+self.width+1)
		self.iw.refresh()
	def addstr(self, string, *args, **kwargs):
		self.log.addstr(string)
		for arg in args:
			self.log.addstr(string+' ')
		self.log.addstr(kwargs.get('end', '\n'))
		self.log.refresh(self.pos, 0, self.windowY, self.windowX, self.windowY+self.height, self.windowX+self.width+1)
		
class NetInput(ScrollWithInput):
	def command(self, string):
		log('COMMAND', string, string=='conn')
		if re.match('host ?.+', string, re.IGNORECASE):
			global HOST
			HOST = re.match('host ?(.+)', string, re.IGNORECASE).groups()[0]
			updateNetstat()
		elif string=='conn':
			log('Connecting')
			global s
			
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))
			log('CONNECTED', str(s))
			l = traa(lyt)
			l.start()
			#ts = traa(tilServer)
			#ts.start()
			updateNetstat()
		elif s: s.send(string.encode('UTF-8'))

class GameInput(ScrollWithInput):
	def command(self, string):
		ipbuf.add(string)
		
class MultiWindow(object):
	def __init__(self, nlines, ncols, y, x):
		self.nlines = nlines
		self.ncols = ncols
		self.y = y
		self.x = x
		self.zones = {}
	def setZone(self, zone, str):
		self.zones[zone].clear()
		try:
			self.zones[zone].addstr(str)
		except curses.error: pass
		self.zones[zone].refresh()
		
class Player(MultiWindow):
	def __init__(self, nlines, ncols, y, x):
		super(Player, self).__init__(nlines, ncols, y, x)
		self.zones = {
			'hand': curses.newwin(math.floor(nlines*3/8), ncols, y, x),
			'play': curses.newwin(math.floor(nlines*3/8), math.floor(ncols/2), y+math.floor(nlines*3/8), x),
			'dcar': curses.newwin(math.floor(nlines*3/8), math.floor(ncols/2), y+math.floor(nlines*3/8), x+math.floor(ncols/2)),
			'stat': curses.newwin(math.floor(nlines/4), math.floor(ncols/2), y+math.floor(nlines*6/8), x),
			'mats': curses.newwin(math.floor(nlines/4), math.floor(ncols/2), y+math.floor(nlines*6/8), x+math.floor(ncols/2)),
		}

class Kingdom(MultiWindow):
	def __init__(self, nlines, ncols, y, x):
		super(Kingdom, self).__init__(nlines, ncols, y, x)
		self.zones = {
			'pile': curses.newwin(math.floor(nlines*3/5), ncols, y, x),
			'even': curses.newwin(math.floor(nlines*2/5), math.floor(ncols/4), y+math.floor(nlines*3/5), x),
			'nspi': curses.newwin(math.floor(nlines*2/5), math.floor(ncols*3/4), y+math.floor(nlines*3/5), x+math.floor(ncols/4)),
		}

class Opponent(MultiWindow):
	def __init__(self, nlines, ncols, y, x):
		super(Opponent, self).__init__(nlines, ncols, y, x)
		self.zones = {
			'play': curses.newwin(math.floor(nlines/2), math.floor(ncols/2), y, x),
			'stat': curses.newwin(math.floor(nlines/2), math.floor(ncols/2), y, x+math.floor(ncols/2)),
			'dcar': curses.newwin(math.floor(nlines/2), math.floor(ncols/2), y+math.floor(nlines/2), x),
			'mats': curses.newwin(math.floor(nlines/2), math.floor(ncols/2), y+math.floor(nlines/2), x+math.floor(ncols/2)),
		}
	
logw = None
cw = None
netstatw = None
trash = None
player = None
kingdom = None
opponent = None
	
def uiup(z, sz, content):
	if z=='play':
		player.setZone(sz, content)
	elif z=='oppo':
		opponent.setZone(sz, content)
	elif z=='tras':
		trash.clear()
		try:
			trash.addstr(content)
		except curses.error: pass
		trash.refresh()
	elif z=='king':
		kingdom.setZone(sz, content)
	
def nstart(stdscr):
	global logw
	global cw
	global netstatw
	global trash
	global player
	global kingdom
	global opponent
	curses.start_color()
	maxY, maxX = stdscr.getmaxyx()
	logw = GameInput(windowX=math.floor(maxX/2), windowY=math.floor(maxY/3), height=math.floor(maxY*2/3)-2, width=maxX-math.floor(maxX/2)-1, scrollDepth=1000)
	cw = NetInput(windowX=math.floor(maxX/4), windowY=math.floor(maxY/8*7), height=maxY-math.floor(maxY/8*7)-2, width=math.floor(maxX/4)-1)
	netstatw = curses.newwin(maxY-math.floor(maxY/8*7), math.floor(maxX/4)-1, math.floor(maxY/8*7), 0)
	trash = curses.newwin(math.floor(maxY/8), math.floor(maxX/2), math.floor(maxY*7/16), 0)
	player = Player(math.floor(maxY*7/16), math.floor(maxX/2), 0, 0)
	kingdom = Kingdom(math.floor(maxY/3), math.floor(maxX/2), 0, math.floor(maxX/2))
	opponent = Opponent(math.floor(maxY*5/16), math.floor(maxX/2), math.floor(maxY*9/16), 0)
	for zone in player.zones: player.setZone(zone, zone)
	for zone in kingdom.zones: kingdom.setZone(zone, zone)
	for zone in opponent.zones: opponent.setZone(zone, zone)
	trash.addstr('trash')
	trash.refresh()	
	while True:
		cw.run()	
		logw.run()
	
def updateNetstat():
	netstatw.clear()
	netstatw.addstr(str(HOST)+', '+str(PORT)+', '+str(s))
	netstatw.refresh()
	
def request(head):
	s.send(('requ'+head).encode('UTF-8'))
		
me = None
		
def updt(signal, **kwargs):
	global me
	if signal=='startTurn':
		logw.addstr('-'*36)
	if signal=='globalSetup':
		if 'you' in kwargs: me = kwargs['you']
	elif signal=='beginRound':
		logw.addstr('*'*36)
	logw.addstr('>'+signal, end='::'+' '*(18-len(signal)))
	for key in kwargs:
		if key=='sender': continue
		logw.addstr(key+': '+str(kwargs[key]), end=', ')
	logw.addstr('')
	
def answer(**kwargs):
	s.send('answ'.encode('UTF-8')+struct.pack('I', testUser(kwargs['options'], kwargs['name'])))
	
def lyt(**kwargs):
	while True:
		try: head = s.recv(4).decode('UTF-8')
		except: continue
		if head=='ques':
			try:
				length = struct.unpack('I', s.recv(4))[0]
				recieved = s.recv(length)
				if not len(recieved)==length:
					logw.addstr('lost package')
					continue
				upickle = pickle.loads(recieved)
			except: continue
			aF = traa(answer, name=upickle[0], options=upickle[1])
			aF.start()
		elif head=='updt':
			try:
				length = struct.unpack('I', s.recv(4))[0]
				recieved = s.recv(length)
				if not len(recieved)==length:
					logw.addstr('lost package')
					continue
				l = pickle.loads(recieved)
			except: continue
			updt(l[0], **l[1])
		elif head=='resp':
			try:
				recieved = s.recv(4)
				if not len(recieved)==4:
					logw.addstr('lost package')
					continue
				length = struct.unpack('I', recieved)[0]
			except: continue
			logw.addstr(s.recv(length).decode('UTF-8'))
		elif head=='uiup':
			try:
				zone = s.recv(4).decode('UTF-8')
				subzone = s.recv(4).decode('UTF-8')
				length = struct.unpack('I', s.recv(4))[0]
				content = s.recv(length).decode('UTF-8')
			except: continue
			uiup(zone, subzone, content)
		
def main():
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	l = traa(lyt)
	l.start()
	ts = traa(tilServer)
	ts.start()


if __name__ == '__main__':
	curses.wrapper(nstart)
	
"""
if __name__=='__main__':
	#HOST = input('connect to: ')
	#if HOST=='': HOST = 'localhost'
	#HOST = 'localhost'
	#HOST = str(socket.gethostbyname(socket.gethostname()))
	#print(HOST)
	main()
"""