import threading
import time

class traa(threading.Thread):
	def __init__(self, f, **kwargs):
		threading.Thread.__init__(self)
		self.f = f
		self.vals = kwargs
	def run(self):
		self.f(**self.vals)

class InputBuffer(object):
	def __init__(self):
		self.lock = threading.Semaphore()
		self.lock.acquire()
		self.value = []
	def get(self):
		if self.value: return self.value.pop()
		else:
			self.lock.acquire()
			return self.value.pop()
	def add(self, value):
		self.value = [value]
		self.lock.release()
		
ipbuf = InputBuffer()
		
def pp():
	while True: print(ipbuf.get())
	
st = traa(pp)
st.start()

while True:
	ipbuf.add(input(': '))