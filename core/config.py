"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/config.py
"""
import json
from core.utils import Utils
from core.ui import UI

class CONFIG:
    
    def __init__(self, path):
        self.configs = {}
        self.path = path
        self.parse_config()
        
    def parse_config(self):
        try:
            self.configs = json.loads(Utils.load_file(self.path, True))
        except:
            UI.error("%s configuration file is not valid" % self.path, True)
            
    def key_exists(self, key):
        if self.configs.has_key(key):
            return True
        return False
            
    def get(self, key):
        if self.key_exists(key):
            return self.configs[key]
        return ""
        
    def set(self, key, value):
        self.configs[key] = value