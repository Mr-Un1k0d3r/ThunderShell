"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/apis.py
"""
import urllib2
import hashlib
import json
import sys

class CliApi:
    
    def __init__(self, config):
        self.config = config
        self.server = self.config["server"]
        
    def ping(self):
        if not self.send_get_request("%s/api/" % self.server):
            return False
        return True
        
    def login(self):
        data = self.send_get_request("%s/api/login" % self.server)
        if not data:
            return False
        
        if data["authorized"] == 1:
            return True
        return False
    
    def send_get_request(self, url):
        request = urllib2.Request(url)
        request.add_header("Authorization", self.config["password"])
        request.add_header("X-Client-Version", self.config["version"])
        
        try:
            return json.loads(urllib2.urlopen(request).read())
        except:
            
            return False
        
class ServerApi:
    
    def __init__(self, config, request):
        self.config = config
        self.request = request
        self.output = {}
        self.output["success"] = 1
        
    def process(self):
        try:
            callback = self.request.path.split("/")[2].lower()
            if callback == "login":
                if self.auth():
                    self.output["authorized"] = 1
                else:
                    self.output["authorized"] = 0
        except:
            pass
        
        return json.dumps(self.output)
        
    def get_header(self, key):
        return self.request.headers.getheader(key)
        
    def auth(self):
        if hashlib.sha512(self.config.get("server-password")).hexdigest() == self.get_header("Authorization"):
            return True
        return False