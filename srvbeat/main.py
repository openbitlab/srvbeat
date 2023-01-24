import os
import sys
import json
import socket

import srvbeat 
from srvbeat.message import Message, MessageParsingError

if sys.version_info[0] < 3:
	print ('python2 not supported, please use python3')
	sys.exit (0)

def saveState(sfile, sdata):
	f = open(sfile, 'w')
	f.write(json.dumps(sdata))
	f.close()


def main():
	version = srvbeat.__version__
	print (f"Starting srvbeat version {version}")
	sfile = os.environ['HOME'] + '/.srvbeat.json'

	try:
		ddata = json.loads(open(sfile, 'r').read())
	except FileNotFoundError as e:
		print ('This is your first run of srvbeat, initializing...')
		ddata = {}
		saveState(sfile, ddata)


	HOST = "127.0.0.1"
	
	if len(sys.argv) > 1:
		PORT = int(sys.argv[1])
	else:
		PORT = 65432

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()

	print ('Srvbeat is now listening for incoming connections')

	while True:
		conn, addr = s.accept()
		conn.settimeout(2.0)

		print(f"Connected by {addr}")

		data = conn.recv(1024)

		if not data:
			conn.sendall(b'er')
			continue 

		try:
			dd = Message.parse(data)
		except:
			conn.sendall(b'pe')
			continue
			
		# Handle message
		print ('received:', dd)

		conn.sendall(b'ok')