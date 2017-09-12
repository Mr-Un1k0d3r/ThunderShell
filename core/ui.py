"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/ui.py
"""
import os
from core.version import Version

class UI:
    
    @staticmethod
    def error(error, die=False):
        print "\n\033[31m[-] %s\033[00m" % error
        if die:
            os._exit(0)

    @staticmethod
    def success(message):
        print "\033[36m[+] %s\033[00m" % message
    
    @staticmethod    
    def prompt(path):
        prompt = "\n\033[32m(%s)>>> \033[00m" % path
        cmd = raw_input(prompt)
        return cmd
    
    @staticmethod
    def banner():
        print "\n\033[32mThunder Shell %s | Clients Server CLI\nMr.Un1k0d3r RingZer0 Team 2017\n--------------------------------------------------------\n\033[00m" % Version.VERSION