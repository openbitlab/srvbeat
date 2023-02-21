class MessageParsingError(Exception):
	pass 

class Message:
	def __init__(self, name, proto, data):
		self.name = name
		self.proto = proto 
		self.data = data

	def __repr__(self):
		return f'name: {self.name}, proto: {self.proto}, pairs: {self.data}'

	def parse(rdata):
		l = rdata.decode('ascii').split('|')

		if l[0] != 'SB' or l[-1] != 'gb':
			raise MessageParsingError('Invalid magics')

		proto = int(l[1])
		name = l[2]
		kps = {}

		if len(l) > 5:
			for x in l[3:-1]:
				xl = x.split(':')
				kps[xl[0]] = xl[1].split(',')

				if len(kps[xl[0]]) == 1:
					kps[xl[0]] = kps[xl[0]][0]

		return Message(name, proto, kps)
		