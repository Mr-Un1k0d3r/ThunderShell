"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/utils.py
"""
import os
import re
import ssl
import glob
import string
import random
import urllib2
import datetime
from core.ui import UI

class Utils:
    VERSION = "1.1"
    
    @staticmethod
    def file_exists(path, die=False, show_error=True):
        if os.path.exists(path):
            return True
        
        if show_error:
            UI.error("%s not found" % path, die)
        return False
    
    @staticmethod
    def load_file(path, die=False, show_error=True):
        if Utils.file_exists(path, die, show_error):
            return open(path, "rb").read()
        return ""
    
    @staticmethod
    def load_file_unsafe(path):
        return open(path, "rb").read()
    
    @staticmethod
    def create_folder_tree(path):
        os.makedirs(path)
        
    @staticmethod
    def unix_to_date(timestamp):
        return datetime.datetime.fromtimestamp(float(timestamp)).strftime('%d/%m/%Y %H:%M:%S')
    
    @staticmethod
    def get_arg_at(cmd, index, max):
        cmd = cmd.split(" ", max)
        if len(cmd) - 1 >= index:
            return cmd[index]
        return ""
    
    @staticmethod
    def download_url(path):
        request = urllib2.Request(path)
        request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0")
        
        # Accept invalid cert
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        data = ""
        try:
            data = urllib2.urlopen(request, context=context).read()
        except:
            UI.error("Failed to fetch %s" % path)
        
        return data
    
    @staticmethod
    def load_powershell_script(path, length):
        data = Utils.load_file("powershell/%s" % path)
        return Utils.update_vars(data, length)
        
    @staticmethod
    def update_vars(data, length):
        for i in reversed(range(0, length + 1)):
            data = data.replace("VAR%d" % i, Utils.gen_str(random.randrange(4, 16)))
        return data   
    
    @staticmethod
    def update_key(data, key, value):
        return data.replace("[%s]" % key, value) 
        
    @staticmethod
    def gen_str(size):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(size)) 
        
    @staticmethod
    def get_download_folder_content():
        files = []
        for item in glob.glob("download/*"):
            files.append(item.replace("download/", ""))
        return files
    
    @staticmethod
    def validate_guid(guid):
        if re.match("^[\w\d]+$", guid):
            return guid
        return ""
    
    @staticmethod
    def check_dependencies():
        try:
            from tabulate import tabulate
            import redis
        except:
            UI.error("Missing depencies. Install (python-redis, python-tabulate)", True)
