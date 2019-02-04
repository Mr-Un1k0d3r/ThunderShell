#!/usr/bin/python
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/rc4.py
"""
import os,re
from Crypto.Cipher import ARC4

class RC4:

	def __init__(self, key):
		self.rc4 = ARC4.new(key)

	def crypt(self, data):
		return self.rc4.encrypt(data)

	def dcrypt(self, data):
		return self.rc4.decrypt(data)

	def gen_rc4_key(size):
		return os.urandom(size)

	def format_rc4_key(key):
		return "0x" + ", 0x".join(re.findall("..", key.encode("hex")))

