
class probMap(list):
	def get(self, val):
		sum = 0
		for i in range(len(self)):
			sum += self[i]
			if val<=sum: return i
		return len(self)-1
		
pm = probMap((0.1, 0.5, 0.4))

print(pm)

print([pm.get(o/10) for o in range(10)])