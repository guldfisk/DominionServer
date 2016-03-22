import threading as t

def f(): print('sup son')

ti = t.Timer(4, f)
ti.start()

i = input(': ')
#ti.cancel()

#while True: continue