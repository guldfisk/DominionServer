
class Log(object):
	def __init__(self, **kwargs):
		self.out = open('log.log', 'a')
	def log(self, *args, end='\n'):
		for arg in args:
			self.out.write(arg)
			self.out.write(end)