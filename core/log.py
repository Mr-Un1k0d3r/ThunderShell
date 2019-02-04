#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/log.py
"""

import time
import base64
from core.utils import Utils


class Log:

    def log_http_request(ip, address, request):
        path = "%shttp.log" % Log.create_folder_tree()
        open(path, "a+").write("[%s] %s (%s) %s\n" % (Utils.timestamp(), ip, address, request))

    def log_shell(guid,type,data,username=None):
        path = "%sshell_%s.log" % (Log.create_folder_tree(), guid)
        if not username == None:
            open(path, "a+").write("""[%s] %s %s: \n%s\n""" % (Utils.timestamp(), username, type, data))
        else:
            open(path, "a+").write("""[%s] %s: \n%s\n""" % (Utils.timestamp(),type, data))

    def log_event(type, data):
        path = "%sevent.log" % Log.create_folder_tree()
        open(path, "a+").write("[%s] %s: %s\n" % (Utils.timestamp(), type, data))

    def log_error(reason, data):
        path = "%serror.log" % Log.create_folder_tree()
        open(path, "a+").write("[%s] %s: %s\n" % (Utils.timestamp(), reason, data))

    def log_chat(timestamp, username, message):
        path = "%schat.log" % Log.create_folder_tree()
        open(path, "a+").write("[%s] Username: %s, Message: %s\n" % (timestamp, username, message))

    def log_screenshot(guid, data):
        path = "%sscreenshot_%s_%s.png" % (Log.create_folder_tree(), Utils.gen_str(8), guid)
        open(path, "wb").write(base64.b64decode(data))

    def create_folder_tree():
        path = Log.get_current_path("")
        if not Utils.file_exists(path, False, False):
            Utils.create_folder_tree(path)
        return path

    def get_current_path(path):
        return "logs/%s/%s" % (Log.get_current_date(), path)

    def get_current_date():
        return time.strftime("%d-%m-%Y")

    def append_keylogger_data(guid, data):
        path = "%skeylogger_%s.log" % (Log.create_folder_tree(), guid)
        open(path, "a+").write(base64.b64decode(data).decode())
