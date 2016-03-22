import socket

class F(object):
	def __init__(self, c):
		self.c = c
	def recvLen(self, l=4):
		bytes = b''
		while len(bytes)<l: bytes += self.c.recv(1)
		return bytes

HOST = 'localhost'
PORT = 6700
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
waitall = F(conn)
while True: print(waitall.recvLen())