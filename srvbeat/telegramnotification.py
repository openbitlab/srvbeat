# MIT License

# Copyright (c) 2023 Openbitlab Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
        except ConnectionError as e:  # noqa: F841
            print("Conncetion error")

    def format(self, name, string):
        return urllib.parse.quote("#" + name + " " + string)

    def getUpdates(self):
        return requests.get(
            f"https://api.telegram.org/bot{self.apiToken}/getUpdates"
        ).json()
