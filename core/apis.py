"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/apis.py
"""
from core.utils import Utils
from core.log import Log
import urllib2
import hashlib
import json
import base64

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
    
    def get_shell_data(self, guid):
        return self.send_get_request("%s/api/shell/%s" % (self.server, guid))
        
    def send_shell_data(self, guid, data):
        return self.send_post_request("%s/api/shell/%s" % (self.server, guid, data))
    
    def send_get_request(self, url):
        return self.send_request(url)
        
    def send_post_request(self, url, data):
        return self.send_request(url, data)
               
    def send_request(self, url, data=None):
        request = urllib2.Request(url)
        request.add_header("Authorization", self.config["password"])
        request.add_header("X-Client-Version", self.config["version"])
        
        try:
            if data == None:
                return json.loads(urllib2.urlopen(request, json.dumps(data)).read())
            else:
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
            elif callback == "list":
                self.get_shells()
            elif callback == "shell":
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
                guid = self.request.path.split("/")[3]
                guid = Utils.validate_guid(guid)
                path = Log.get_current_path("shell_%s.log" % guid)
                data = Utils.load_file(path, False, False)
                self.output["data"] = base64.b64encode(data)
            except:
                return 
            
    def send_shell_cmd(self):
        if self.auth():
            try:
                guid = self.request.path.split("/")[3]
                guid = Utils.validate_guid(guid)
                self.db.push_cmd(guid, self.get_post_data())
            except:
                return
            
    def get_post_data(self):
        length = 0
        if not self.headers.getheader("Content-Length") == None:
            length = int(self.headers.getheader("Content-Length"))
        return self.rfile.read(length)