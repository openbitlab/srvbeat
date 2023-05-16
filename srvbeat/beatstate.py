import json
import time
import sys
import traceback
from datetime import datetime
from threading import Thread, Lock

from .message import Message

HELP_STR = """Commands:
\t/help: shows this help
\t/mute name [t]: mute the node name for t minutes (default: 60)
\t/unmute name: unmute the node name
\t/forget name: forget the node by name
\t/list: returns the nodes list
\t/testcall: test a call to the default number
\t/enablecall name: enable calls for the node name
\t/disablecall name: disable calls for the node name
"""

class BeatState:
	def __init__(self, sfile, conf, tg, tw):
		self.conf = conf
		self.tg = tg
		self.tw = tw

		self.callAfter = int(conf['general']['callAfter'])
		self.beatTimeout = int(conf['general']['beatTimeout'])

		self.sfile = sfile
		self.pthread = None
		self.cthread = None
		self.slock = Lock()
		self.running = True
		self.muted = {} 
		self.callMem = {}

		# Load state file
		try:
			self.data = json.loads(open(self.sfile, 'r').read())
		except FileNotFoundError as e:
			print ('This is your first run of srvbeat, initializing...')
			self.data = {
				'telegram': {
					'lastUpdateId': 0
				},
				'nodes': {}
			}
			self.save()

		self.tg.send(f'❤️ Srvbeat started: 🕑 beatTimeout is {self.beatTimeout} sec, ☎ calls are {"enabled" if self.tw else "disabled"}')

	def save(self):
		""" Save current state """
		f = open(self.sfile, 'w')
		f.write(json.dumps(self.data))
		f.close()

	def forget(self, name):
		""" Forget a server """
		if name not in self.data['nodes']:
			self.tg.send(f'❓{name} is not a known node')
			return 

		del self.data['nodes'][name]
		self.save()

		self.tg.send(f'🔌 {name} forgotten')

	def unmute(self, name, dmin):
		""" Unmute a server """			
		if name not in self.data['nodes']:
			self.tg.send(f'❓{name} is not a known node')
			return 
				
		del self.muted[name]
		self.tg.send(f'🔈 {name} unmuted')

	def mute(self, name, dmin):
		""" Mute a server """			
		if name not in self.data['nodes']:
			self.tg.send(f'❓{name} is not a known node')
			return 
				
		self.muted[name] = time.time() + (dmin * 60)
		self.tg.send(f'🔇 muted {name} for {dmin} minutes (until {datetime.fromtimestamp(self.muted[name])})')

	def checkMuted(self, name):
		""" Check if a server is muted """
		if name not in self.muted:
			return False
		
		if self.muted[name] < time.time():
			del self.muted[name]
			self.tg.send(f'🔈 {name} not muted anymore')
			return False

		return True		

	def changeCallEnable(self, name, s):
		if name not in self.data['nodes']:
			self.tg.send(f'❓{name} is not a known node')
			return False

		self.slock.acquire()	
		self.data['nodes'][name]['callEnabled'] = s
		self.save()
		self.slock.release()
		return True

	def enableCall(self, name):
		if self.changeCallEnable(name, True):
			self.tg.send(f'☎ Call enabled for node {name}')

	def disableCall(self, name):
		if self.changeCallEnable(name, False):
			self.tg.send(f'☎ Call disabled for node {name}')

	def isCallEnabled(self, name):
		if name not in self.data['nodes']:
			return False
		return self.data['nodes'][name]['callEnabled']

	def feed(self, message):
		""" Feed a new message to the beatState """
		self.slock.acquire()

		# Discovered a new server
		if message.name not in self.data['nodes']:
			self.tg.send(f'🔗 discovered a new server: {message.name}')
			self.data['nodes'][message.name] = {
				'name': message.name,
				'lastMessage': message.data,
				'lastBeat': time.time(),
				'status': 'online',
				'callEnabled': True
			}

		else:
			self.data['nodes'][message.name]['lastMessage'] = message.data

			olds = self.data['nodes'][message.name]['status']
			if olds != 'online':
				cbt = int((time.time()-self.data['nodes'][message.name]['lastBeat']) / 60.)
				self.tg.send(f'✅ {message.name} come back online after {cbt} minutes')

				# Reset call memory
				if message.name in self.callMem:
					del self.callMem[message.name]
			self.data['nodes'][message.name]['status'] = 'online'
			self.data['nodes'][message.name]['lastBeat'] = time.time()

		self.save()
		self.slock.release()


	def _nodeLine (self, x):
		l = ('✅' if x['status'] == 'online' else '🔴')
		if self.checkMuted(x['name']):
			l += '🔇'
		l += ' ' + x['name']
		l += f' ({int((time.time() - x["lastBeat"])/60)} minutes ago)'

		return l

	def _checkLoop(self):
		time.sleep(120)
		i = 0

		while self.running:
			i += 1

			self.slock.acquire()

			if i % 60 == 1:
				cc = list(map(self._nodeLine, self.data['nodes'].values()))
				ccs = '\n'.join(cc)
				self.tg.send(f'📥 I\'m still alive, don\'t worry.\n{ccs}', False)

			# Check for delayed beats
			for name in self.data['nodes']:
				n = self.data['nodes'][name]

				if (n['lastBeat'] + self.beatTimeout) < time.time():
					wasonline = self.data['nodes'][name]['status'] == 'online'
					self.data['nodes'][name]['status'] = 'offline'

					since = int ((time.time() - n["lastBeat"]) / 60)
					if wasonline or not self.checkMuted(n['name']):
						self.tg.send(f'🔴 {name} is not sending a beat since {since} minutes')

					# Perform a phone call
					if self.tw and since > self.callAfter and (name not in self.callMem) and self.isCallEnabled(name):
						try:
							cid = self.tw.call()
							self.tg.send(f'☎ Emergency call submitted after {since} minutes: {cid}')
							self.callMem[x] = time.time()
						except:
							self.tg.send(f'☎ Error while performing a phone call')
							print (traceback.format_exc())
							
					self.save()
					
			self.slock.release()
			sys.stdout.flush()
			time.sleep(60)


	def _polling(self):
		firstPool = True 

		while self.running:
			# Get and handle telegram updates
			try:
				up = self.tg.getUpdates()
			except:
				time.sleep(20)
				continue

			if not up['ok']:
				time.sleep(5)
				continue 

			self.slock.acquire()
			
			# Get results and filter
			r = up['result']
			r = list(filter(lambda x: x['update_id'] > self.data['telegram']['lastUpdateId'] and str(x['message']['chat']['id']) == self.tg.chatId, r))

			if firstPool:
				if len(r) > 0:
					self.data['telegram']['lastUpdateId'] = r[-1]['update_id']
					self.save()
				r = list(filter (lambda x: x['message']['date'] > int(time.time()), r))
				firstPool = False 

			if len(r) > 0:
				self.data['telegram']['lastUpdateId'] = r[-1]['update_id']
				self.save()

			r = list(filter(lambda x: 'text' in x['message'], r))
			r = list(map(lambda x: x['message']['text'], r))


			# If I'm not the master, skip message handling
			if not bool(self.conf['general']['master'] == 'true'):
				self.slock.release()
				continue 

			for x in r:
				if x[0] != '/':
					continue 

				xx = x.split(' ')

				if xx[0] == '/help':
					self.tg.send(HELP_STR)

				elif xx[0] == '/forget' and len(xx) == 2:
					self.forget(xx[1])

				elif xx[0] == '/testcall':
					i = self.tw.call()
					self.tg.send(f'☎ Test call submitted: {cid}')

				elif xx[0] == '/disablecall' and len(xx) == 2:
					v = xx[1]
					self.disableCall(v, dmin)

				elif xx[0] == '/enablecall' and len(xx) == 2:
					v = xx[1]
					self.enableCall(v, dmin)

				elif xx[0] == '/mute' and len(xx) >= 2:
					v = xx[1]
					dmin = 60
					if len(xx) == 3:
						if xx[2][-1].isdigit():
							dmin = int(xx[2]) 
						elif xx[2][0::-1].isdigit():
							dmin = int(xx[2][0::-1])
							u = xx[2][-1]
							if u == 'h':
								dmin *= 60
							elif u == 'd':
								dmin *= 24 * 60
					self.mute(v, dmin)		

				elif xx[0] == '/unmute' and len(xx) == 2:
					v = xx[1]
					self.unmute(v)			

				elif xx[0] == '/list':
					cc = list(map(self._nodeLine, self.data['nodes'].values()))

					if len(cc) == 0:
						self.tg.send('nothing here yet')
					else:
						self.tg.send('\n'.join(cc))

				else:
					self.tg.send(f'unrecognized command: ```{str(x)}```')


			self.slock.release()
			sys.stdout.flush()
			time.sleep(10)

	def startPolling(self):
		self.pthread = Thread(target=self._polling, args=[])
		self.pthread.start()

		self.cthread = Thread(target=self._checkLoop, args=[])
		self.cthread.start()


	def stop(self):
		self.running = False
		self.pthread.join()
		self.cthread.join()
