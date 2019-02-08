#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/shell.py
"""
from tabulate import tabulate
from core.alias import Alias

class Shell:

    def __init__(self, cli = False):
        self.cli = cli
        
    def init_cmds(self):
        self.cmds = {}
        self.cmds['help'] = self.help
        self.cmds['fetch'] = self.fetch
        self.cmds['read'] = self.read_file
        self.cmds['upload'] = self.upload_file
        self.cmds['delay'] = self.update_delay
        self.cmds['exec'] = self.exec_code
        self.cmds['ps'] = self.ps
        self.cmds['inject'] = self.inject
        self.cmds['alias'] = self.set_alias
        self.cmds['background'] = None
        self.cmds['keylogger'] = self.keylogger
        self.cmds['exit'] = None
        self.alias = Alias()
        
    def evalute_cmd(self, cmd):
        self.cmd = cmd
        cmd = self.cmd.split(' ', 1)[0].lower()
        
        if not self.cmds.has_key(cmd):
            return cmd
        
        callback = self.cmds[cmd]
        callback()
        
    def help(self):
        output = '''Help Menu\n''' + '=' * 9 + \
        '\n' + tabulate({'Commands': [
            'background',
            'fetch',
            'exec',
            'read',
            'upload',
            'ps',
            'inject',
            'keylogger',
            'alias',
            'delay',
            'help',
            ],
            'Args': [
            '',
            '',
            'path/url, cmd',
            'path/url',
            'remote path',
            'path/url, path',
            'pid, command',
            'number of line (default 20)',
            'key, value',
            'milliseconds',
            ],
            'Descriptions': [
            'Return to the main console (CLI only)',
            'In memory execution of a script and execute a command',
            'In memory execution of code (shellcode)',
            'Read a file on the remote host',
            'Upload a file on the remote system',
            'List processes',
            'Inject command into a target process (max length 4096)',
            'Show last n line of keystrokes captured',
            'Create an alias to avoid typing the same thing over and over',
            'Update the callback delay',
            'show this help menu',
            ]},
            headers='keys', tablefmt='simple')
        output += self.alias.list_alias()
        output += self.alias.list_custom_alias()
        return output