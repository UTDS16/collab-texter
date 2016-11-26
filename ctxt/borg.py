# Based on Alex Martelli's singleton pattern (called Borg)
# http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html

"""
A singleton, named "Borg".
"""
class Borg:
	# Internals of the single class instance.
	_shared_state = {}

	def __init__(self):
		# Every new instance gets the same state as the first one.
		self.__dict__ = self._shared_state

	@staticmethod
	def get_instance():
		"""
	Gets the one and only instance of the class.
	"""
		return Borg()
