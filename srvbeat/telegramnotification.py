import os
import json
import requests
import urllib.parse
from etcd3 import Client

class TelegramNotification:
	def __init__(self, conf):
		self.apiToken = conf['telegram']['apiToken'].strip('\"')
		self.chatId = conf['telegram']['chatId'].strip('\"')
		self.client_etcd = Client(conf['general']['etcdEndpoint'], 2379)
		self.etcd_id = self.client_etcd.status().header.member_id

	def sendPhoto(self, photo):
		os.system('curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s' % (photo, self.apiToken, self.chatId))

	def send(self, st, notify = True):
		print(st.encode('utf-8'))
		args = f"text={st}&chat_id={self.chatId}"
		if not notify:
			args += '&disable_notification=true'
		if self.etcd_id == self.client_etcd.status().leader:
			requests.get(f'https://api.telegram.org/bot{self.apiToken}/sendMessage?{args}').json()

	def format(self, name, string):
		return urllib.parse.quote('#' + name + ' ' + string)

	def getUpdates(self):
		return requests.get(f'https://api.telegram.org/bot{self.apiToken}/getUpdates').json()
