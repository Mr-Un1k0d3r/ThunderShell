#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/sync.py
"""

import threading
import time
from core.ui import UI

class Sync:

    def __init__(self, config):
        self.config = config
        self.sql = self.config.get('mysql')
        self.redis = self.config.get('redis')

    def get_cmd_send(self, uid):
        try:
            guid = False
            cmd = ""
            for item in self.sql.get_cmd(uid):
                data = self.sql.get_cmd_data(item[1])
                self.sql.delete_cmd(item[0], item[2], item[1], item[3])
                cmd += "%s Sending: \n%s" % (item[4],data)
            return cmd
        except IndexError:
            pass

    def get_cmd_output(self, guid, uid):
        cmd_output = ""
        for item in self.sql.get_cmd_response(uid):
            self.sql.delete_response(item[0], item[2], item[1], item[3])
            cmd_output += '%s\n' % self.redis.get_output(item[0], item[1])[0]
        return cmd_output

def start_cmd_sync(config):
    sync = Sync(config)
    thread = threading.Thread(target=start_cmd_sync_thread, args=(sync,))
    thread.start()

def start_cmd_sync_thread(sync, uid):
    delay = 0
    try:
        delay = float(sync.config.get('cli-sync-delay'))
    except:
        UI.error('"cli-sync-delay" should be an integer check your config')
        delay = 5
    while True:
        guid = sync.get_cmd_send(uid)
        guid = sync.get_cmd_output(guid)
        if guid:
            sync.get_prompt(guid)
        time.sleep(delay)
