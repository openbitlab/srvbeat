class TwilioCallNotification:
	def __init__(self, conf):
		self.account_sid = conf['twilio']['accountSid']
		self.auth_token = conf['twilio']['authToken']
		self.toNumber = conf['twilio']['to']
		self.fromNumber = conf['twilio']['from']
	
	def call(self):
		from twilio.rest import Client
		client = Client(self.account_sid, self.auth_token)

		call = client.calls.create(
			url='http://demo.twilio.com/docs/voice.xml',
			to=self.toNumber,
			from_=self.fromNumber
		)

		return call.sid
