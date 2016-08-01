import curses
import time
import threading
import curses.textpad
import sys
import os
import math
import socket
import threading		
import struct
import pickle
import re
import json

s = None
name = None
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
	
def testUser(options, name='noName', source=None):
	if not name=='buySelection':
		st = '-?'+name
		if not source=='None': st+='('+source+')'
		logw.addstr(st, end=': ')
		for option in options: logw.addstr(gN(option), end=', ')
	else: logw.addstr('-?---Choose buy---')
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
		self.escaped = True
	def validation(self, c):
		#if c==ord('q'): sys.exit()
		if c==curses.KEY_UP:
			if not self.pos<1: self.pos -= 1
			self.refresh()
			#log(self.pos)
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
			if not self.running: continue
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
	def setName(self, n):
		sendPack(s, 'NAME', {'name': n})
	def command(self, string):
		#log('COMMAND', string, string=='conn')
		if re.match('host ?.+', string, re.IGNORECASE):
			global HOST
			HOST = re.match('host ?(.+)', string, re.IGNORECASE).groups()[0]
			updateNetstat()
		elif string=='conn':
			global s
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))
			l = traa(lyt)
			l.start()
			if name: self.setName(name)
			updateNetstat()
		#elif string=='conc':
		#	ipbuf.add('')
		#	s.send(string.encode('UTF-8'))
		elif re.match('name ?.+', string, re.IGNORECASE):
			n = re.match('name ?(.+)', string, re.IGNORECASE).groups()[0]
			if s: self.setName(n)
			else:
				global name
				name = n
		elif s and re.match('game.*', string, re.IGNORECASE):
			m = re.match('game(.+)', string, re.IGNORECASE)
			if m: k = m.groups()[0]
			else: k = ''
			sendPack(s, 'GAME', {'kingdom': k})
		elif s and string=='debu': sendPack(s, 'DEBU')
		elif s and string=='rupd': sendPack(s, 'RUPD')
		elif s and string=='rque': sendPack(s, 'RQUE')
		elif s and string=='reco': sendPack(s, 'RECO')
		elif s and string=='conc': sendPack(s, 'CONC')
		
class GameInput(ScrollWithInput):
	def command(self, string):
		ipbuf.add(string)
		
class MultiWindow(dict):
	def __init__(self, nlines, ncols, y, x):
		self.nlines = nlines
		self.ncols = ncols
		self.y = y
		self.x = x
	def upw(self, key, st):
		self[key].clear()
		try: self[key].addstr(st)
		except curses.error: pass
		self[key].refresh()
	def upd(self, d):
		pass
	
def lcts(cards):
	def gs(c):
		if 'owner' in c and c['owner']: return c['name']+'('+c['owner']+')'
		else: return c['name']
	ud = ''
	names = [gs(c) for c in cards]
	unames = set(names)
	for name in unames: ud+=str(names.count(name))+' '+name+', '
	return ud
	
def pts(pile):
	if 'cards' in pile: return lcts(pile['cards'])
	return 'length: '+str(pile['length'])
	
def statts(d):
	ud = ''
	for key in sorted(d):
		if type(d[key])==dict: ud += key+': '+str(d[key]['length'])+', '
		else: ud += key+': '+str(d[key])+', '
	return ud
	
def matsts(d):
	ud = ''
	for key in sorted(d):
		ud += key+': '+pts(d[key])+'\n'
	return ud
	
def pilests(d):
	ud = ''
	for key in sorted(d):
		ud += d[key]['card']['name']+': '+str(d[key]['length'])+' '+str(d[key]['card']['c'])+'$'
		if d[key]['card']['p']: ud += str(d[key]['card']['p'])+'P'
		if d[key]['card']['d']: ud += str(d[key]['card']['d'])+'D'
		if d[key]['tokens']['cards']:
			ud += '('+pts(d[key]['tokens'])+')'
		ud += ', '
	return ud
	
def eventsts(d):
	ud = ''
	for key in sorted(d):
		ud += key+' '+str(d[key]['c'])+'$'
		if d[key]['p']: ud += str(d[key]['p'])+'P'
		if d[key]['d']: ud += str(d[key]['d'])+'D'
		if d[key]['tokens']['cards']: ud+= '('+pts(d[key]['tokens'])+')'
		ud += ', '
	return ud

def landsts(d):
	ud = ''
	for key in sorted(d):
		ud += key
		if d[key]['tokens']['cards']: ud+= '('+pts(d[key]['tokens'])+')'
		ud += ', '
	return ud
	
class Player(MultiWindow):
	def __init__(self, nlines, ncols, y, x):
		super(Player, self).__init__(nlines, ncols, y, x)
		self.update({
			'hand': curses.newwin(math.floor(nlines*3/8), ncols, y, x),
			'inPlay': curses.newwin(math.floor(nlines*3/8), math.floor(ncols/2), y+math.floor(nlines*3/8), x),
			'discardPile': curses.newwin(math.floor(nlines*3/8), math.floor(ncols/2), y+math.floor(nlines*3/8), x+math.floor(ncols/2)),
			'values': curses.newwin(math.floor(nlines/4), math.floor(ncols/2), y+math.floor(nlines*6/8), x),
			'mats': curses.newwin(math.floor(nlines/4), math.floor(ncols/2), y+math.floor(nlines*6/8), x+math.floor(ncols/2)),
		})
	def upd(self, d):
		if 'hand' in d: self.upw('hand', pts(d['hand']))
		if 'inPlay' in d: self.upw('inPlay', pts(d['inPlay']))
		if 'discardPile' in d: self.upw('discardPile', pts(d['discardPile']))
		if 'values' in d: self.upw('values', statts(d['values']))
		if 'mats' in d: self.upw('mats', matsts(d['mats']))

class Kingdom(MultiWindow):
	def __init__(self, nlines, ncols, y, x):
		super(Kingdom, self).__init__(nlines, ncols, y, x)
		self.update({
			'piles': curses.newwin(math.floor(nlines*3/5), ncols, y, x),
			'events': curses.newwin(math.floor(nlines*2/5), math.floor(ncols/4), y+math.floor(nlines*3/5), x),
			'nonSupplyPiles': curses.newwin(math.floor(nlines*2/5), math.floor(ncols*3/4), y+math.floor(nlines*3/5), x+math.floor(ncols/4)),
		})
	def upd(self, d):
		if 'piles' in d: self.upw('piles', pilests(d['piles']))
		eventlands = ''
		if 'events' in d: eventlands += eventsts(d['events'])
		if 'landmarks' in d: eventlands += landsts(d['landmarks'])+'\n'
		self.upw('events', eventlands)
		if 'nonSupplyPiles' in d: self.upw('nonSupplyPiles', pilests(d['nonSupplyPiles']))
		
class Opponent(MultiWindow):
	def __init__(self, nlines, ncols, y, x):
		super(Opponent, self).__init__(nlines, ncols, y, x)
		self.update({
			'inPlay': curses.newwin(math.floor(nlines/2), math.floor(ncols/2), y, x),
			'values': curses.newwin(math.floor(nlines/2), math.floor(ncols/2), y, x+math.floor(ncols/2)),
			'discardPile': curses.newwin(math.floor(nlines/2), math.floor(ncols/2), y+math.floor(nlines/2), x),
			'mats': curses.newwin(math.floor(nlines/2), math.floor(ncols/2), y+math.floor(nlines/2), x+math.floor(ncols/2)),
		})
	def upd(self, d):
		if 'inPlay' in d: self.upw('inPlay', pts(d['inPlay']))
		if 'discardPile' in d: self.upw('discardPile', pts(d['discardPile']))
		if 'values' in d: self.upw('values', statts(d['values']))
		if 'mats' in d: self.upw('mats', matsts(d['mats']))
	
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
	trash.addstr('trash')
	trash.refresh()
	if os.path.exists('cccnfg.cfg'):
		with open('cccnfg.cfg', 'r') as f:
			for ln in f.read().splitlines(): cw.command(ln)
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
	sendPack(s, 'ANSW', {'index': testUser(kwargs['options'], kwargs['name'], kwargs['source'])})
	#s.send(struct.pack('I', testUser(kwargs['options'], kwargs['name'])))
	
def recvLen(s, l=4):
	bytes = b''
	while len(bytes)<l: bytes += s.recv(1)
	return bytes
	
def recvPack(s):
	head = recvLen(s).decode('UTF-8')
	l = struct.unpack('>I', recvLen(s))[0]
	if l: body = json.loads(recvLen(s, l).decode('UTF-8'))
	else: body = {}
	return head, body
	
def sendPack(s, head, content=None):
	h = head.encode('UTF-8')
	assert (len(h)==4), 'Wrong head length'
	if content: st = json.dumps(content).encode('UTF-8')
	else: st = b''
	i = struct.pack('>I', len(st))
	s.send(h+i+st)
	
def lyt(**kwargs):
	while True:
		head, body = recvPack(s)
		if head=='QUES':
			aF = traa(answer, name=body['name'], options=body['options'], source=body['source'])
			aF.start()
		elif head=='UPDT':
			player.upd(body['player'])
			kingdom.upd(body['kingdom'])
			if body['opponents']:
				#print(body['opponents'])
				opponent.upd(body['opponents'][list(body['opponents'])[0]])
			trash.clear()
			try:
				trash.addstr(pts(body['kingdom']['trash']))
			except curses.error: pass
			trash.refresh()
		elif head=='NLOG':
			n = body.pop('name')
			updt(n, **body)
		
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
