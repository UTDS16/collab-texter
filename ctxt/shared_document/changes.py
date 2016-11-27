from abc import ABCMeta, abstractmethod


class Change:
	def __init__(self):
		pass

	__metaclass__ = ABCMeta

	@abstractmethod
	def apply(self, text):
		"""
		Apply this change to a text.

		Parameters
		----------
		text : str

		Returns
		-------
		str : modified text
		"""
		pass

	@abstractmethod
	def rebase(self, other_change):
		"""
		Update this Change to come after another change.
		The update is applied in-place.

		Parameters
		----------
		other_change : Change
		"""
		pass


class Insert(Change):
	def __init__(self, pos, text):
		"""
		Parameters
		----------
		pos : int
			Index of the position where the `text` will be inserted.
			After insertion the new text will start from `pos`.
		text : str
			Text to insert.
		"""
		super(Insert, self).__init__()
		assert pos >= 0
		assert len(text) > 0
		self.pos = pos
		self.text = text

	def apply(self, text):
		assert self.pos >= 0
		assert self.pos <= len(text)
		return text[:self.pos] + self.text + text[self.pos:]

	def rebase(self, other_change):
		raise NotImplementedError


class Delete(Change):
	def __init__(self, start_pos, end_pos):
		"""
		Parameters
		----------
		start_pos : int
			The start of the range of characters to be deleted. Inclusive.
		end_pos : int
			The end of the range of characters to be deleted. Inclusive.
		"""
		super(Delete, self).__init__()
		assert start_pos >= 0
		assert start_pos <= end_pos
		self.start_pos = start_pos
		self.end_pos = end_pos

	def apply(self, text):
		assert self.start_pos >= 0
		assert self.start_pos <= self.end_pos
		assert self.end_pos < len(text)
		return text[:self.start_pos] + text[self.end_pos + 1:]

	def rebase(self, other_change):
		raise NotImplementedError
