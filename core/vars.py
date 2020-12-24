#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/vars.py
"""
import pathlib

class THUNDERSHELL:
    BASE_PATH = pathlib.Path().absolute()
    DATA_PATH = "%s/data" % BASE_PATH
    DOWNLOAD_PATH = "%s/download/" % BASE_PATH
    POWERSHELL_SCRIPT = "%s/powershell/" % DATA_PATH
    PAYLOADS_PATH = "%s/payloads/" % DATA_PATH
    DATA_BIN_PATH = "%s/bin/" % DATA_PATH
    