"""
Utility functions, classes and the like.
"""

import random
import string

"""
Generate a random string consisting of letters and numbers.
"""
def gen_random_string(length):
	return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

"""
Converts data to hex string.
"""
def to_hex_str(data):
	data = bytearray(data)
	return ' '.join("{:02X}".format(x) for x in data)

"""
Check if a unicode character is printable.
"""
def u_is_printable(c):
	try:
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
