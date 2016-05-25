class et:
	def f(self):
		print('et')

class to:
	def f(self):
		print('to')

class tre(to):
	def __init__(self):
		super(tre, self).f()
		
tre()