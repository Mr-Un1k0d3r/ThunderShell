#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Tazz0 RingZer0 Team
    @package: core/autocomplete.py
"""


class Completer(object):

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            return self.matches[state]
        except IndexError:
            return None
