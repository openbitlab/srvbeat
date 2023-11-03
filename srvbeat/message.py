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

class MessageParsingError(Exception):
    pass


class Message:
    def __init__(self, name, proto, data):
        self.name = name
        self.proto = proto
        self.data = data

    def __repr__(self):
        return f"name: {self.name}, proto: {self.proto}, data: {self.data}"

    # TODO:
    # def encode(self, message):

    def parse(rdata):
        if isinstance(rdata, str):
            msg = rdata
        else:
            msg = rdata.decode("ascii")
        msg_l = msg.split("|")

        if msg_l[0] != "SB" or msg_l[-1] != "gb":
            raise MessageParsingError("Invalid magics")

        proto = int(msg_l[1])
        name = msg_l[2]
        kps = {}

        if len(msg_l) > 4:
            for x in msg_l[3:-1]:
                xl = x.split(":")
                kps[xl[0]] = xl[1].split(",")

                if len(kps[xl[0]]) == 1:
                    kps[xl[0]] = kps[xl[0]][0]

        return Message(name, proto, kps)
