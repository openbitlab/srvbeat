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
            self.tg.send(f'❓{name} is not a known node')
            return 

        del self.data['nodes'][name]
        self.save()

        self.tg.send(f'🔌 {name} forgotten')

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
                'status': 'online'
            }

        else:
            self.data['nodes'][message.name]['lastMessage'] = message.data

            olds = self.data['nodes'][message.name]['status']
            if olds != 'online':
                cbt = int((time.time()-self.data['nodes'][message.name]['lastBeat']) / 60.)
                self.tg.send(f'✅ {message.name} come back online after {cbt} minutes')
            self.data['nodes'][message.name]['status'] = 'online'
            self.data['nodes'][message.name]['lastBeat'] = time.time()

        self.save()
        self.slock.release()

    def _polling(self):
        def cl (x):
            l = ('✅' if x['status'] == 'online' else '🔴')
            l += ' ' + x['name']
            l += f' ({int((time.time() - x["lastBeat"])/60)} minutes ago)'

            return l


        firstPool = True 
        i = 0

        while True:
            i += 1

            if i % (750 * 2) == 1:
                cc = list(map(cl, self.data['nodes'].values()))
                ccs = '\n'.join(cc)
                self.tg.send(f'📥 I\'m still alive, don\'t worry.\n{ccs}')

            # Check for delayed beats
            if i % 60 == 1:
                for x in self.data['nodes']:
                    n = self.data['nodes'][x]

                    if (n['lastBeat'] + 300) < time.time():
                        self.data['nodes'][x]['status'] = 'offline'
                        self.tg.send(f'🔴 {n["name"]} is not sending a beat since {int ((time.time() - n["lastBeat"]) / 60)} minutes')


            # Get and handle telegram updates
            up = self.tg.getUpdates()

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

            r = list(map(lambda x: 'text' in x['message'] and x['message']['text'], r))


            # If I'm not the master, skip message handling
            if not self.conf['general']['master']:
                self.slock.release()
                continue 

            for x in r:
                xx = x.split(' ')

                if xx[0] == '/help':
                    self.tg.send('Commands:\n\t/help: shows this help\n\t/forget name: forget the node by name\n\t/list: returns the nodes list')

                elif xx[0] == '/forget':
                    self.forget(xx[1])
                
                elif xx[0] == '/list':
                    cc = list(map(cl, self.data['nodes'].values()))

                    if len(cc) == 0:
                        self.tg.send('nothing here yet')
                    else:
                        self.tg.send('\n'.join(cc))



            self.slock.release()
            time.sleep(5)

    def startPolling(self):
        self.pthread = Thread(target=self._polling, args=[])
        self.pthread.start()
