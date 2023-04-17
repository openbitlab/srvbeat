class TwilioCallNotification:
	def __init__(self, conf):
		account_sid = conf['twilio']['accountSid']
		auth_token = conf['twilio']['authToken']
		toNumber = conf['twilio']['to']
		fromNumber = conf['twilio']['from']
	
	def call(self):
		from twilio.rest import Client
		client = Client(self.account_sid, self.auth_token)

		call = client.calls.create(
			url='http://demo.twilio.com/docs/voice.xml',
			to=self.toNumber,
			from_=self.fromNumber
		)

		return call.sid
