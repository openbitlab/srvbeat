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


def sendUsageBeat(host, port, name):
	Bash = srvcheck.utils.bash.Bash

	mp = '/'
	uptime = Bash('uptime').value().split('up ')[1].split(',')[0]
	diskSize = int(Bash(f'df {mp}').value().split('\n')[1].split()[1])
	diskUsed = int(Bash(f'df {mp}').value().split('\n')[1].split()[2])
	diskPercentageUsed = float(Bash(f'df {mp}').value().split('\n')[1].split()[4].replace('%', ''))
	diskUsedByLog = int(Bash('du /var/log').value().rsplit('\n', 1)[-1].split()[0])

	ramSize = int(Bash('free').value().split('\n')[1].split()[1])
	ramUsed = int(Bash('free').value().split('\n')[1].split()[2])
	ramFree = int(Bash('free').value().split('\n')[1].split()[4])

	cpuUsage = float(Bash('top -b -n 1 | grep Cpu').value().split()[1].replace(',', '.'))
	u = {
		'CPU': cpuUsage,
		'RAM': ramUsed,
		'DISK': [diskSize, diskUsed, diskPercentageUsed]
	}
	sendBeat(host, port, name, u)


def sendUsageBeatPeriodically(host, port, name, delay):
	def dff():
		while True:
			sendUsageBeat(host, port, name)
			time.sleep(delay)

	t = Thread(target=dff, args=())
	t.start()
	return t

def testClient():
	import sys 

	HOST = "127.0.0.1"

	if len(sys.argv) > 1:
		PORT = int(sys.argv[1])
	else:
		PORT = 65432

	data = sendBeat(HOST, PORT, 'bitcoin-node', {'CPU': 50, 'RAM': 55, 'DISK': [23,54,86]})

	print(f"Received {data!r}")
