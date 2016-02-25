
class clist(list):
	def __init__(self, *args, **kwargs):
		super(clist, self).__init__(*args)
		self.faceup = kwargs.get('faceup', True)
	def multi(self):
		for ele in self:
			ele += 1
			print(ele)
	def p(self):
		print(self, self.faceup)
	
ml = clist()

print(ml)
ml.append(2)
ml.p()