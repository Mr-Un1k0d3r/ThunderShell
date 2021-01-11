# -*- coding: utf-8 -*-

"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/notify.py
"""

import base64 
from core.utils import Utils
from core.vars import THUNDERSHELL


class Modules:

    @staticmethod
    def get_module(name):
        path = "%s%s.exe" % (THUNDERSHELL.MODULES_PATH, name)
        if Utils.file_exists(path):
            return base64.b64encode(Utils.load_file(path)).decode()

    @staticmethod
    def gen_push_command(name):
        return "module %s %s" % (name, Modules.get_module(name))
