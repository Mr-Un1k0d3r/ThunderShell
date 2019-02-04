#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/ui.py
"""

import os
import sys
from core.version import Version


class Colors:

    Yellow = "\033[33m"
    White = "\033[00m"
    Blue = "\033[34m"
    Green = "\033[32m"
    Red = "\033[36m"
    Gray = "\033[1;30m"

class UI:

    @staticmethod
    def error(error, die=False):
        print("\n\033[31m[-] %s\033[00m" % error)
        if die:
            os._exit(0)

    @staticmethod
    def success(message):
        print("\033[32m[+] %s\033[00m" % message)

    @staticmethod
    def warn(message):
        print("\033[33m[*] %s\033[00m" % message)

    @staticmethod
    def prompt(path):
        prompt = "\n\033[32m(%s)>>> \033[00m" % path
        cmd = input(prompt)
        return cmd

    @staticmethod
    def prompt_no_input(path):
        prompt = "\n\033[32m(%s)>>> \033[00m" % path
        sys.stdout.write(prompt)
        sys.stdout.flush()

    @staticmethod
    def banner():
        print("""
             {}.#"{}    {}=[{} ThunderShell version {} | RingZer0 Team {}]={}
           {}.##"{}
        {}.###"{}       __       __    _________    __            __
       {}###P{}        {}###{}|     {}###{}|  {}##########{}|  {}###{}|          {}###{}|
     {}d########"{}    {}###{}|     {}###{}|  {}###{}|         {}###{}|          {}###{}|
     {}****####"{}     {}###{}|_____{}###{}|  {}###{}|__       {}###{}|          {}###{}|
       {}.###"{}       {}############{}|  {}######{}|      {}###{}|          {}###{}|
      {}.##"{}         {}###{}|     {}###{}|  {}###{}|         {}###{}|          {}###{}|
     {}.#"{}           {}###{}|     {}###{}|  {}###{}|______   {}###{}|_______   {}###{}|_______
    {}."{}             {}###{}|     {}###{}|  {}##########{}|  {}###########{}|  {}###########{}|


        """.format(
            Colors.Yellow,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Version.VERSION,
            Colors.Gray,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Yellow,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            Colors.Gray,
            Colors.White,
            ))
