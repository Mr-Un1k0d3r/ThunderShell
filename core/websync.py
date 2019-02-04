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
        self.redis = self.config.get("redis")

    def get_cmd_send(self, uid, id):
        try:
            cmd = ""
            for item in self.redis.get_active_gui_session_cmd(uid, id):
                data = self.redis.get_session_cmd(item)
                data = data.decode()
                data = data.split(":")
                cmd += "%s - Sending command: %s" % (data[0],data[1])
                self.redis.delete_entry(item)
            return cmd
        except IndexError:
            pass

    def get_cmd_output(self, uid, id):
        cmd_output = ""
        for item in self.redis.get_active_gui_session_output(uid, id):
            data = self.redis.get_session_output(item)
            cmd_output += "%s\n" % data.decode()
            self.redis.delete_entry(item)
        return cmd_output
