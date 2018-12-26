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

    def get_cmd_send(self):
        guid = False
        for item in self.sql.get_cmd(self.config.get('uid')):
            print ''
            data = self.sql.get_cmd_data(item[1])
            UI.success('%s - Sending command: %s' % (item[4], data))
            self.sql.delete_cmd(item[0], item[2], item[1], item[3])
            guid = item[0]
            if data == 'exit':
                guid = 'exit'
        return guid

    def get_cmd_output(self, guid):
        for item in self.sql.get_cmd_response(self.config.get('uid')):
            print ''
            UI.warn('Command output:\n%s' % self.redis.get_output(item[0], item[1])[0])
            self.sql.delete_response(item[0], item[2], item[1], item[3])
            guid = item[0]
        return guid

    def get_prompt(self, guid):
        if not guid == 'exit':
            UI.prompt_no_input(self.redis.get_data('%s:prompt' % guid))
        else:
            UI.prompt_no_input('Main')


def start_cmd_sync(config):
    sync = Sync(config)
    thread = threading.Thread(target=start_cmd_sync_thread, args=(sync,))
    thread.start()


def start_cmd_sync_thread(sync):
    delay = 0
    try:
        delay = float(sync.config.get('cli-sync-delay'))
    except:
        UI.error('"cli-sync-delay" should be an integer check your config')
        delay = 5
    while True:
        guid = sync.get_cmd_send()
        guid = sync.get_cmd_output(guid)
        if guid:
            sync.get_prompt(guid)
        time.sleep(delay)
