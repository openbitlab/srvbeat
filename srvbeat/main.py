import os
import sys
import json
import time
import socket
import argparse
import configparser
import traceback

import srvbeat 
from srvbeat.beatstate import BeatState
from srvbeat.message import Message, MessageParsingError
from srvbeat.telegramnotification import TelegramNotification
from srvbeat.twiliocallnotification import TwilioCallNotification

if sys.version_info[0] < 3:
	print ('python2 not supported, please use python3')
	sys.exit (0)

def _linearize(e, cc = {}, xx = ''):
	for x in e:
		if isinstance(e[x], dict):
			cc = _linearize(e[x], cc, (xx + '.' + x) if (xx != '') else x)
		else:
			cc[xx + ('.' if xx != '' else '') + x] = e[x]
	return cc

def main():
	cf = '/etc/srvbeat.conf'
	parser = argparse.ArgumentParser(description='Srvbeat')
	parser.add_argument('--config', type=str, default=cf, help='srvbeat config file')
	args = parser.parse_args()
	cf = args.config

	version = srvbeat.__version__
	print (f"Starting srvbeat version {version}")

	# Parse configuration
	cc = configparser.ConfigParser()
	cc.optionxform=str
	cc.read(cf)
	conf = _linearize(cc)


	# Setup telegram
	tg = TelegramNotification(conf)

	# Setup twilio
	tw = TwilioCallNotification(conf) if conf['general']['callEnabled'] else None

	# Setup beatstate        
	sfile = os.environ['HOME'] + '/.srvbeat.json'
	bs = BeatState(sfile, conf, tg, tw)

	# Bind the server
	HOST = ""
	
	if len(sys.argv) > 1:
		PORT = int(sys.argv[1])
	else:
		PORT = 65432

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connected = False

	while not connected:
		try:
			s.bind((HOST, PORT))
			s.listen()
			connected = True
		except:
			print ("Address in use, waiting...")
			time.sleep(10)

	print ('Srvbeat is now listening for incoming connections on port %d' % PORT)

	# Mainloop
	bs.startPolling()

	while True:
		conn, addr = s.accept()
		conn.settimeout(2.0)

		print(f"Connected by {addr}")

		try:  
			data = conn.recv(1024)
		except socket.error:  
			print ('Socket error, skipping')
			continue

		if not data:
			conn.sendall(b'er')
			continue 

		try:
			dd = Message.parse(data)
		except:
			print(traceback.format_exc())
			conn.sendall(b'pe')
			continue

		# Handle message
		print ('received:', dd)
		
		try:
			bs.feed(dd)
		except:
			print(traceback.format_exc())
			conn.sendall(b'fe')
			continue
			

		conn.sendall(b'ok')
		sys.stdout.flush()

	bs.stop()