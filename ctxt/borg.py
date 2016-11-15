# Alex Martelli's singleton pattern (called Borg)
# http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html

class Borg:
	_shared_state = {}

	def __init__(self):
		self.__dict__ = self._shared_state
	
