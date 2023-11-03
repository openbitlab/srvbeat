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

import socket
import time
from threading import Thread


def sendBeat(host, port, name, pairs):
    # TODO: move to message.encode
    ps = []
    for x in pairs:
        if isinstance(pairs[x], list):
            ps.append("%s:%s" % (x, ",".join(list(map(lambda x: str(x), pairs[x])))))
        else:
            ps.append("%s:%s" % (x, str(pairs[x])))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        st = "SB|1|%s|%s|gb" % (name, "|".join(ps))
        s.sendall(bytes(st, "ascii"))
        data = s.recv(1024)
        s.close()
    return data


def sendBeatPeriodically(host, port, name, delay):
    def dff():
        while True:
            sendBeat(host, port, name, {})
            time.sleep(delay)

    t = Thread(target=dff, args=())
    t.start()
    return t


def standaloneClient():
    import sys

    if len(sys.argv) < 4:
        print("usage: srvbeat-client name host port")
        return

    NAME = sys.argv[1]
    HOST = sys.argv[2]
    PORT = int(sys.argv[3])

    sendBeat(HOST, PORT, NAME, {})


def testClient():
    import sys

    HOST = "127.0.0.1"

    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])
    else:
        PORT = 65432

    data = sendBeat(
        HOST, PORT, "bitcoin-node", {"CPU": 50, "RAM": 55, "DISK": [23, 54, 86]}
    )

    print(f"Received {data!r}")
