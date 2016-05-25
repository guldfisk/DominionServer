import copy

class Wrapper(object):
	def __init__(self, obj):
		self.obj = obj

	def __getattr__(self, attr):
		if attr in self.__dict__:
			return getattr(self, attr)
		return getattr(self.obj, attr)

class base:
	def __init__(self):
		if not hasattr(self, 'types'): self.types = []
		self.val = None
	def bad(self):
		print('hot shit')
	def setVal(self, val):
		self.val = val
		
class et(base):
	def bad(self):
		print('Det er et', self)
		
class to(base):
	def bad(self):
		print('Det er to', self)
		
e = Wrapper(et())
t = Wrapper(to())

print(e, t)

print(e.val, t.val)

e.setVal(2)

print(e.obj.val, t.val)