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
        path = f"{THUNDERSHELL.MODULES_PATH}/{name}.exe"
        if Utils.file_exists(path):
            return base64.b64encode(Utils.load_file(path))

    @staticmethod
    def gen_push_command(name):
        return f"module {name} {Modules.get_module(name)}"
