import socket 


def sendBeat(host, port, name, pairs):
	ps = []
	for x in pairs.keys():
		ps += '%s:%s' % (x, str(pairs[x]))

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((host, port))
		s.sendall(b("SB|1|%s|%s|gb" % (name, '|'.join(ps))))
		data = s.recv(1024)
		s.close()
	return data


def testClient():
	import sys 

	HOST = "127.0.0.1"

	if len(sys.argv) > 1:
		PORT = int(sys.argv[1])
	else:
		PORT = 65432

	data = sendBeat(HOST, PORT, 'bitcoin-node', {'CPU': 50, 'RAM': 55, 'DISK': [23,54,86]})

	print(f"Received {data!r}")
