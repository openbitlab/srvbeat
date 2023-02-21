from threading import Thread
import socket 

def sendBeat(host, port, name, pairs):
	ps = []
	for x in pairs:
		if type(pairs[x]) == list:
			ps.append('%s:%s' % (x, ','.join(list(map(lambda x: str(x), pairs[x])))))
		else:
			ps.append('%s:%s' % (x, str(pairs[x])))

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((host, port))
		st = "SB|1|%s|%s|gb" % (name, '|'.join(ps))
		s.sendall(bytes(st, 'ascii'))
		data = s.recv(1024)
		s.close()
	return data


def sendBeatPeriodically(host, port, name, delay):
	def dff():
		while True:
			sendBeat(host, port, name, {})
			time.sleep(delay)

	t = Thread(target=dff, args=())
	t.start()
	return t


def standaloneClient():
	import sys 

	if len(sys.argv) < 4:
		print ("usage: srvbeat-client name host port")
		return

	NAME = sys.argv[1]
	HOST = sys.argv[2]
	PORT = int(sys.argv[3])

	sendBeat(HOST, PORT, NAME, {})


def testClient():
	import sys 

	HOST = "127.0.0.1"

	if len(sys.argv) > 1:
		PORT = int(sys.argv[1])
	else:
		PORT = 65432

	data = sendBeat(HOST, PORT, 'bitcoin-node', {'CPU': 50, 'RAM': 55, 'DISK': [23,54,86]})

	print(f"Received {data!r}")
