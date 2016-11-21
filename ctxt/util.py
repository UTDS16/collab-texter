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

