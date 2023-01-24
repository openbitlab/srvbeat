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

		for x in l[3:-1]:
			xl = x.split(':')
			kps[xl[0]] = xl[1].split(',')

		return Message(name, proto, kps)
		