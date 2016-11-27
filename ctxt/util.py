"""
Utility functions, classes and the like.
"""

import random
import string

def gen_random_string(length):
	"""
	Generate a random string consisting of letters and numbers.
	"""
	return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def to_hex_str(data):
	"""
	Converts data to hex string.
	"""
	data = bytearray(data)
	return ' '.join("{:02X}".format(x) for x in data)

def u_is_printable(c):
	"""
	Check if a unicode character is printable.
	"""
	try:
		if c == "":
			return False
		# Is the character printable?
		if c in string.printable:
			return True

		# Try unicode printables as well.
		ic = ord(c)
		if ic >= 0x00BF and ic <= 0xFFFF:
			return True
	except TypeError as e:
		pass
	return False

def i_is_printable(i):
	"""
	Check if an integer keycode refers to a printable character.
	"""
	if i >= 0x20 and i < 0xBF and chr(i) in string.printable:
		return True
	if i >= 0x00BF and i <= 0xFFFF:
		return True
	return False
