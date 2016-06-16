

class d(dict):
	def __init__(self):
		self.update({
			'wow': 1,
			'damn': 'son'
		})
	def p(self):
		for k in self: print(k, self[k])
		
class l(list):
	def __init__(self):
		self = [1, 2, 3]
	def p(self):
		print('wow', self)
		
b = d()



b.p()

print(b)

ll = l()

ll.p()

print(ll)