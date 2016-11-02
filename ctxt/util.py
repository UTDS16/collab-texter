"""
Utility functions, classes and the like.
"""

import random

"""
Generate a random string consisting of letters and numbers.
"""
def gen_random_string(length):
	return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
