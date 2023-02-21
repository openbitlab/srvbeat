import os
import json
import requests
import urllib.parse

class TelegramNotification:
	def __init__(self, conf):
		self.apiToken = conf['telegram']['apiToken'].strip('\"')
		self.chatId = conf['telegram']['chatId'].strip('\"')

	def sendPhoto(self, photo):
		os.system('curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s' % (photo, self.apiToken, self.chatId))

	def send(self, st):
		print(st.encode('utf-8'))
		requests.get(f'https://api.telegram.org/bot{self.apiToken}/sendMessage?text={st}&chat_id={self.chatId}').json()

	def format(self, name, string):
		return urllib.parse.quote('#' + name + ' ' + string)

	def getUpdates(self):
		return requests.get(f'https://api.telegram.org/bot{self.apiToken}/getUpdates').json()
