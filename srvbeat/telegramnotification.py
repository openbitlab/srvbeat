import json
import os
import urllib.parse

import requests
from requests.exceptions import ConnectionError


class TelegramNotification:
    def __init__(self, conf):
        self.apiToken = conf["telegram"]["apiToken"].strip('"')
        self.chatId = conf["telegram"]["chatId"].strip('"')

    def sendPhoto(self, photo):
        os.system(
            'curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s'
            % (photo, self.apiToken, self.chatId)
        )

    def send(self, st, notify=True):
        print(st.encode("utf-8"))
        args = f"text={st}&chat_id={self.chatId}"
        if not notify:
            args += "&disable_notification=true"
        try:
            requests.get(
                f"https://api.telegram.org/bot{self.apiToken}/sendMessage?{args}"
            ).json()
        except ConnectionError as e:
            print("Conncetion error.")

    def format(self, name, string):
        return urllib.parse.quote("#" + name + " " + string)

    def getUpdates(self):
        return requests.get(
            f"https://api.telegram.org/bot{self.apiToken}/getUpdates"
        ).json()
