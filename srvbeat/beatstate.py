import json
import time
from threading import Thread, Lock

from .message import Message

class BeatState:
    def __init__(self, sfile, conf, tg):
        self.conf = conf
        self.tg = tg
        self.sfile = sfile
        self.pthread = None
        self.slock = Lock()

        # Load state file
        try:
            self.data = json.loads(open(self.sfile, 'r').read())
        except FileNotFoundError as e:
            print ('This is your first run of srvbeat, initializing...')
            self.data = {
                'telegram': {
                    'lastUpdateId': 0
                },
                'peers': {}
            }
            self.save()

    def save(self):
        """ Save current state """
        f = open(self.sfile, 'w')
        f.write(json.dumps(self.data))
        f.close()

    def forget(self, name):
        """ Forget a server """
        if name not in self.data['peers']:
            return 

        del self.data['peers'][name]
        self.save()

        self.tg.send(f'{name} forgotten')

    def feed(self, message):
        """ Feed a new message to the beatState """
        self.slock.acquire()

        # Discovered a new server
        if message.name not in self.data:
            self.tg.send(f'discovered a new server: {message.name}')
            self.data['peers'][message.name] = {
                'name': message.name,
                'lastMessage': message,
                'lastBeat': time.time(),
                'status': 'online'
            }

        else:
            self.data['peers'][message.name]['lastMessage'] = message

            olds = self.data['peers'][message.name]['status']
            if olds != 'online':
                cbt = int(time.time()-self.data['peers'][message.name]['lastBeat']) / 60.
                self.tg.send(f'{message.name} come back online after {cbt} minutes')
            self.data['peers'][message.name]['status'] = 'online'
            self.data['peers'][message.name]['lastBeat'] = time.time()

        self.save()
        self.slock.release()

    def _polling(self):
        while True:
            up = self.tg.getUpdates()

            if not up['ok']:
                time.sleep(5)
                continue 

            self.slock.acquire()
            r = up['result']
            r = list(filter(lambda x: x['update_id'] > self.data['telegram']['lastUpdateId'] and str(x['message']['chat']['id']) == self.tg.chatId, r))

            if len(r) > 0:
                self.data['telegram']['lastUpdateId'] = r[-1]['update_id']
                self.save()

            r = list(map(lambda x: x['message']['text'], r))

            print(r)

            self.slock.release()
            time.sleep(5)

    def startPolling(self):
        self.pthread = Thread(target=self._polling, args=[])
        self.pthread.run()