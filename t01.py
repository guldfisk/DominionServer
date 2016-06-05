

def wow(**kwargs):
	print(kwargs)
	kwargs.pop('et', None)
	print(kwargs)


d = {'et': 1, 'to': 2}

wow(**d)