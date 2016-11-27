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

		Returns
		-------
		list(Change) : list of changes that this change is transformed to by rebasing.
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
		self._pos = pos
		self._text = text

	@property
	def pos(self):
		return self._pos

	@property
	def text(self):
		return self._text

	def apply(self, text):
		assert self.pos <= len(text)
		return text[:self.pos] + self.text + text[self.pos:]

	def rebase(self, other_change):
		assert isinstance(other_change, Change)
		if isinstance(other_change, Insert):
			return self._rebase_over_insert(other_change)
		elif isinstance(other_change, Delete):
			return self._rebase_over_delete(other_change)

	def _rebase_over_insert(self, other_insert):
		if other_insert.pos <= self.pos:
			new_insert = Insert(self.pos + len(other_insert.text),
			                    self.text)
			return [new_insert]
		return [self]

	def _rebase_over_delete(self, other_delete):
		if other_delete.start_pos <= self.pos <= other_delete.end_pos:
			new_insert = Insert(self.pos + other_delete.start_pos,
			                    self.text)
			return [new_insert]
		elif other_delete.end_pos < self.pos:
			new_insert = Insert(self.pos - other_delete.end_pos - other_delete.start_pos + 1,
			                    self.text)
			return [new_insert]
		return [self]


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
		self._start_pos = start_pos
		self._end_pos = end_pos

	@property
	def start_pos(self):
		return self._start_pos

	@property
	def end_pos(self):
		return self._end_pos

	def apply(self, text):
		assert self.end_pos < len(text)
		return text[:self.start_pos] + text[self.end_pos + 1:]

	def rebase(self, other_change):
		assert isinstance(other_change, Change)
		if isinstance(other_change, Insert):
			self._rebase_over_insert(other_change)
		elif isinstance(other_change, Delete):
			self._rebase_over_delete(other_change)

	def _rebase_over_insert(self, other_insert):
		if self.start_pos < other_insert.pos <= self.end_pos:
			# The newer insert is inside the delete region.
			# Need to split the delete in two.
			new_delete1 = Delete(self.start_pos,
			                     other_insert.pos - 1)
			new_delete2 = Delete(other_insert.pos + len(other_insert.text),
			                     self.end_pos + len(other_insert.text))
			return [new_delete1, new_delete2]
		if other_insert.pos <= self.start_pos:
			shift = len(other_insert.text)
			new_delete = Delete(self.start_pos - shift,
			                    self.end_pos - shift)
			return [new_delete]
		return [self]

	def _rebase_over_delete(self, other_delete):
		shift = other_delete.end_pos - other_delete.start_pos + 1
		# To clarify each branch
		# a - character deleted by this
		# b - character deleted by other
		# x - deleted by both
		if other_delete.end_pos < self.start_pos:
			# bbbaaa
			new_delete = Delete(self.start_pos - shift,
			                    self.end_pos - shift)
			return [new_delete]
		if self.start_pos <= other_delete.start_pos and other_delete.end_pos <= self.end_pos:
			# axxxa
			new_delete = Delete(self.start_pos,
			                    self.end_pos - shift)
			return [new_delete]
		if self.start_pos < other_delete.start_pos and self.end_pos >= other_delete.end_pos:
			# aaxxbb
			new_delete = Delete(self.start_pos,
			                    other_delete.start_pos - 1)
			return [new_delete]
		if other_delete.start_pos <= self.start_pos and self.end_pos <= other_delete.end_pos:
			# bxxxb
			return []
		if other_delete.start_pos < self.start_pos and other_delete.end_pos >= self.end_pos:
			# bbxxaa
			new_delete = Delete(other_delete.start_pos,
			                    self.end_pos - shift)
			return [new_delete]
