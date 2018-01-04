"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/apis.py
"""
from core.utils import Utils
import urllib2
import hashlib
import json

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
    
    def list_shell(self):
        return self.send_get_request("%s/api/list" % self.server)
    
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
        self.db = self.config.get("redis")
        self.output = {}
        self.output["success"] = 1
        
    def process(self):
        try:
            callback = self.request.path.split("/")[2].lower()
            if callback == "login":
                self.auth()
            if callback == "list":
                self.get_shells()
            if callback == "shell":
                self.get_shell_output()    
            
        except:
            pass
        
        return json.dumps(self.output)
        
    def get_header(self, key):
        return self.request.headers.getheader(key)
        
    def auth(self):
        if hashlib.sha512(self.config.get("server-password")).hexdigest() == self.get_header("Authorization"):
            self.output["authorized"] = 1
            return True
        self.output["authorized"] = 0
        return False
    
    def get_shells(self):
        if self.auth():
            shells = []
            for shell in self.db.get_all_shells():
                guid = shell.split(":")[0]
                prompt = self.db.get_data("%s:prompt" % guid)
                shells.append("%s %s" % (guid, prompt))
        
            self.output["shells"] = shells
            
    def get_shell_output(self):
        if self.auth():
            try:
                shell_id = self.request.path.split("/")[3]
            except:
                return 