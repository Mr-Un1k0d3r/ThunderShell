"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/config.py
"""
import json
from core.utils import Utils
from core.ui import UI

class CONFIG:
    DEFAULT_INSTALL_PATH = "install.lock"    


    def __init__(self, path):
        self.configs = {}
        self.path = path
        self.parse_config()
        self.reload = False
	self.gen_encryption_key()

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

    def gen_encryption_key(self):
        install = Utils.file_exists(CONFIG.DEFAULT_INSTALL_PATH, False)
	if not install:
		self.set("encryption-key", Utils.gen_str(24))
		self.set("server-password", Utils.gen_str(32))
		open(CONFIG.DEFAULT_INSTALL_PATH, "wb").write("OK")
		self.save_config()
		self.reload = True

    def save_config(self):
	data = json.dumps(self.configs, indent=4, sort_keys=True)
	open(self.path, "wb").write(data)

    def reload_config(self):
	return self.reload
