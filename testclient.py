import socket

HOST = 'localhost'
PORT = 6700

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
	
while True: s.send(input(': ').encode('UTF-8'))