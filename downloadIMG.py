import requests
import json

basePath = 'http://dominion.diehrstraits.com/scans/'

cards = json.loads(open('cards.json', 'r').read())

print(cards)

for key in cards:
	for card in cards[key]:
		if not key=='baseSet': continue
		c = card.replace(' ', '').replace("'", '').replace('/', '').lower()
		r = requests.get(basePath+'base'+'/'+c+'.jpg')
		print(basePath+key+'/'+c+'.jpg')
		with open('img\\'+c+'.jpg', 'wb') as fd:
			for chunk in r.iter_content(1024):
				fd.write(chunk)