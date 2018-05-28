from socket import socket


def createContext(ip, port) :
	sock = socket()
	sock.connect((ip, port))
	return sock


def mainClient(sock) :
	print sock.recv(1024)
	sock.send('je suis le client')


if __name__ == '__main__' :
	sock = createContext('127.0.0.1', 1234)
	mainClient(sock)