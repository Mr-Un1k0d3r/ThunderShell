#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/alias.py
"""


class Alias:

    def __init__(self):
        self.alias = {}
        self.alias["wmiexec"] = \
            ("https://raw.githubusercontent.com/Mr-Un1k0d3r/RedTeamPowershellScripts/master/scripts/Remote-WmiExecute.ps1"
             , "Remote-WmiExecute utility")
        self.alias["searchevent"] = \
            ("https://github.com/Mr-Un1k0d3r/RedTeamPowershellScripts/blob/master/scripts/Search-EventForUser.ps1"
             , "Search-EventForUser utility")
        self.custom_alias = {}

    def get_alias(self, alias):
        return self.is_alias(alias)

    def is_alias(self, alias):
        if alias.lower() in self.alias:
            return self.alias[alias][0]
        if alias.lower() in self.custom_alias:
            return self.custom_alias[alias]
        return alias

    def get_all_alias(self):
        return list(self.alias.keys())

    def get_all_custom_alias(self):
        return list(self.custom_alias.keys())

    def get_description(self, alias):
        return self.alias[alias][1]

    def get_custom_description(self, alias):
        return self.custom_alias[alias]

    def get_customs(self):
        return self.custom_alias

    def set_custom(self, key, value):
        self.custom_alias[key] = value

    def list_alias(self):
        output = "\n\nList of built in aliases\n%s\n" % ("-" * 24)
        for key in self.get_all_alias():
            output += "%s%s%s\n" % (key, " " * (28 - len(key)), self.get_description(key))
        return output

    def list_custom_alias(self):
        output = "\n\nList user defined aliases\n%s\n" % ("-" * 26)
        for key in self.get_all_custom_alias():
            output += "%s%s%s\n" % (key, " " * (28 - len(key)), self.get_custom_description(key))
        return output
