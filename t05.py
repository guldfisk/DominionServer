import re

king = 'det, er, sick, 12 wow, 56amn'

for c in re.finditer('(\d+)? ?([a-z]+)', king, re.IGNORECASE):
	amnt, cont = c.groups()
	print(amnt, cont)