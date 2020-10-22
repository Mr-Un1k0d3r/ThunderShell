#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/utils.py
"""

import os
import re
import sys
import ssl
import time
import uuid
import glob
import string
import random
import requests
import platform
import urllib.request, urllib.error, urllib.parse
import datetime

from core.vars import THUNDERSHELL
from core.ui import UI
from core.version import Version

class Utils:

    @staticmethod
    def suppress_ssl_errors():
        requests.packages.urllib3.disable_warnings() 

    @staticmethod
    def start_redis():
        if not os.getuid() == 0:
            UI.error("root privileges required to install force start redis server")
        os.system("/usr/bin/redis-server /etc/redis/redis.conf")

    @staticmethod
    def url_decode(url):
        return urllib.parse.unquote(url)

    @staticmethod
    def timestamp():
        return str(time.strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def file_exists(path, die=False, show_error=True):
        if os.path.exists(path):
            return True

        if show_error:
            UI.error("%s not found" % path, die)
        return False

    @staticmethod
    def load_file(path, die=False, show_error=True):
        if Utils.file_exists(path, die, show_error):
            return open(path, "rb").read()
        return ""

    @staticmethod
    def load_file_unsafe(path):
        return open(path, "rb").read()

    @staticmethod
    def create_folder_tree(path):
        os.makedirs(path)

    @staticmethod
    def unix_to_date(timestamp):
        return datetime.datetime.fromtimestamp(float(timestamp)).strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def get_arg_at(cmd, index, max):
        cmd = cmd.split(" ", max)
        if len(cmd) - 1 >= index:
            return cmd[index]
        return ""

    @staticmethod
    def download_url(path):
        request = urllib.request.Request(path)
        request.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0")

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        data = ""
        try:
            data = urllib.request.urlopen(request, context=context).read().decode()
        except:
            UI.error("Failed to fetch %s" % path)

        return data

    @staticmethod
    def load_powershell_script(path, length):
        data = Utils.load_file(path).decode()
        return Utils.update_vars(data, length)

    @staticmethod
    def update_vars(data, length):
        for i in reversed(list(range(0, length + 1))):
            data = str(data).replace("VAR%d" % i, Utils.gen_str(random.randrange(4, 16)))
        return data

    @staticmethod
    def update_key(data, key, value):
        return data.replace("[%s]" % key, value)

    @staticmethod
    def gen_str(size):
        return "".join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(size))

    @staticmethod
    def get_download_folder_content():
        files = []
        for item in glob.glob("%s/*" % THUNDERSHELL.DOWNLOAD_PATH):
            files.append(item.replace(THUNDERSHELL.DOWNLOAD_PATH, ""))
        return files

    @staticmethod
    def validate_guid(guid):
        if re.match("^[\w\d]+$", guid):
            return guid
        return ""

    @staticmethod
    def guid():
        return str(uuid.uuid4())

    @staticmethod
    def check_dependencies():
        try:
            from tabulate import tabulate
            from flask_socketio import SocketIO
            from Crypto.Cipher import ARC4
            import flask
            import redis
        except Exception as e:
            UI.error("Missing dependencies", False)
            Utils.install_dependencies("3")
            if "-install3.6" in sys.argv:
                UI.error("Installing python 3.6", False)
                Utils.install_dependencies("3.6")
            if "-install3.7" in sys.argv:
                UI.error("Installing python 3.7", False)
                Utils.install_dependencies("3.7")
            UI.error("Installation completed! Please restart ThunderShell", True)
 
    @staticmethod
    def check_version():
        current = Version.VERSION
        request = urllib.request.Request("http://thundershell.ringzer0team.com/version.html?%s" % current)
        response = urllib.request.urlopen(request).read().strip().decode()
        if not response == current:
            UI.error("Your ThunderShell installation is outdated latest is %s. Your version is %s" % (response, current), False) 
            UI.warn("Do you want to exit ThunderShell and update it") 
            if UI.prompt('Updating (Yes/No)').lower() == 'yes':
                os.system("git pull")
                UI.error("Installation updated! Please restart ThunderShell", True)
                os._exit(0)
       
    @staticmethod
    def install_dependencies(pyver):
        UI.warn("Installing dependencies")
        if not os.getuid() == 0:
            UI.error("root privileges required to install the dependencies")
        os.system("/usr/bin/apt update && /usr/bin/apt install redis-server mono-mcs python%s python%s-pip python%s-dev -y" % (pyver, pyver, pyver))
        os.system("pip%s install tabulate" % pyver)
        os.system("pip%s install redis" % pyver)
        os.system("pip%s install flask" % pyver)
        os.system("pip%s install flask-socketio" % pyver)
        os.system("pip%s install pycrypto" % pyver)
        os.system("pip%s install gevent" % pyver)

    @staticmethod
    def parse_random(data):
        for item in re.findall("{{random}}\[.{2}\]", data):
            size = 16
            try:
                size = int(re.findall("[0-9]{2}", item)[0])
            except:
                pass

            data = data.replace(item, Utils.gen_str(size))

        return data

    @staticmethod
    def check_pyver():
        if int(platform.python_version().split(".")[1]) < 6:
            UI.error("Please use python >= 3.6", False)
            UI.error("You may want to force ThunderShell to install python3.6 or python3.7 using the following switch (-install3.6, -install3.7", True)
