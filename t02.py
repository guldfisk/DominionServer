import threading


class traa(threading.Thread):
	def __init__(self, f, **kwargs):
		threading.Thread.__init__(self)
		self.f = f
		self.vals = kwargs
	def run(self):
		self.f(**self.vals)

llock = threading.Semaphore()
llock.acquire()

l = []

def iF():
	while True: 
		l.append(input(': '))
		llock.release()
		
		
def getValue():
	while True:
		if not l:
			print('no l')
			llock.acquire()
			print('lock released')
		print(l.pop())
		
iT = traa(iF)
iT.start()

gT = traa(getValue)
gT.start()
