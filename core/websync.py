#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/sync.py
"""

import threading
import datetime
from core.ui import UI
from base64 import b64decode
from core.utils import Utils


class Sync:

    def __init__(self, config):
        self.config = config
        self.redis = self.config.get("redis")

    def get_cmd_send(self, uid, id):
        cmd = ""
        guid = False
        for item in self.redis.get_active_gui_session_cmd(uid, id):
            item = item.decode()
            data = self.redis.get_data(item).decode()
            data = data.split(":", 1)
            guid = item.split(":")[2]
            cmd += "\n[%s] %s - Sending command: %s" % (Utils.timestamp(), data[0], data[1])
            self.redis.delete_entry(item)
        return cmd

    def get_cmd_output(self, uid, id):
        cmd_output = ""
        for item in self.redis.get_active_gui_session_output(uid, id):
            data = self.redis.get_session_output(item)
            cmd_output += "\n[%s] Received output:\n%s" % (Utils.timestamp(),b64decode(data.decode()).decode())
            self.redis.delete_entry(item)
        return cmd_output

