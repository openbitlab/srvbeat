import os
import json
import requests
import urllib.parse

class TelegramNotification:
	def __init__(self, conf):
		super().__init__(conf)
		try:
			self.apiToken = conf['telegram']['apiToken'].strip('\"')
			self.chatIds = conf['telegram']['chatIds'].strip('\"')

		except:
			self.apiToken = ""
			self.chatIds = ""

	def sendPhoto(self, photo):
		for ci in self.chatIds:
			os.system('curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s' % (photo, self.apiToken, ci))

	def send(self, st):
		print(st.encode('utf-8'))
		for x in self.chatIds:
			requests.get(f'https://api.telegram.org/bot{self.apiToken}/sendMessage?text={st}&chat_id={x}').json()

	def format(self, name, string):
		return urllib.parse.quote('#' + name + ' ' + string)

	def polling(self):
		pass