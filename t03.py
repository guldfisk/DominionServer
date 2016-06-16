import json

d = None

s = json.dumps(d)

print(s)

rd = json.loads(s)

print(rd)