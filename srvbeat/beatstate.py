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
                'nodes': {}
            }
            self.save()

    def save(self):
        """ Save current state """
        f = open(self.sfile, 'w')
        f.write(json.dumps(self.data))
        f.close()

    def forget(self, name):
        """ Forget a server """
        if name not in self.data['nodes']:
            self.tg.send(f'{name} is not a known node')
            return 

        del self.data['nodes'][name]
        self.save()

        self.tg.send(f'{name} forgotten')

    def feed(self, message):
        """ Feed a new message to the beatState """
        self.slock.acquire()

        # Discovered a new server
        if message.name not in self.data:
            self.tg.send(f'discovered a new server: {message.name}')
            self.data['nodes'][message.name] = {
                'name': message.name,
                'lastMessage': message,
                'lastBeat': time.time(),
                'status': 'online'
            }

        else:
            self.data['nodes'][message.name]['lastMessage'] = message

            olds = self.data['nodes'][message.name]['status']
            if olds != 'online':
                cbt = int(time.time()-self.data['nodes'][message.name]['lastBeat']) / 60.
                self.tg.send(f'{message.name} come back online after {cbt} minutes')
            self.data['nodes'][message.name]['status'] = 'online'
            self.data['nodes'][message.name]['lastBeat'] = time.time()

        self.save()
        self.slock.release()

    def _polling(self):
        while True:
            up = self.tg.getUpdates()

            if not up['ok']:
                time.sleep(5)
                continue 

            self.slock.acquire()

            # Get results and filter
            r = up['result']
            r = list(filter(lambda x: x['update_id'] > self.data['telegram']['lastUpdateId'] and str(x['message']['chat']['id']) == self.tg.chatId, r))

            if len(r) > 0:
                self.data['telegram']['lastUpdateId'] = r[-1]['update_id']
                self.save()

            r = list(map(lambda x: x['message']['text'], r))


            # If I'm not the master, skip message handling
            if not self.conf['general']['master']:
                self.slock.release()
                continue 

            for x in r:
                xx = x.split(' ')

                if xx[0] == '/help':
                    self.tg.send('Commands:\n\t/help: shows this help\n\t/forget name: forget the node by name\n/list: returns the nodes list')

                elif xx[0] == '/forget':
                    self.forget(xx[1])
                
                elif xx[0] == '/list':
                    cc = list(map(lambda x: x.name, self.data['nodes'].values()))

                    if len(cc) == 0:
                        self.tg.send('nothing here yet')
                    else:
                        self.tg.send('\n'.join(cc))



            self.slock.release()
            time.sleep(5)

    def startPolling(self):
        self.pthread = Thread(target=self._polling, args=[])
        self.pthread.run()