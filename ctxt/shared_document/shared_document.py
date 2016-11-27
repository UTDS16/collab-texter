"""
Document class.
"""

import logging

import ctxt.util as cu

from .changes import *


class Commit:
	"""
	Attributes
	----------
	parent :
	changes : list[Change]
	"""

	def __init__(self, parent):
		"""

		Parameters
		----------
		parent
		"""
		self.changes = []

	def rebase(self, other_commit):
		"""
		Update the changes in this commit to come after the `other_commit`.

		Parameters
		----------
		other_commit : Commit
		"""
		for other_change in other_commit.changes:
			for change in self.changes:
				change.rebase(other_change)


class ChangeLog:
	"""
	Attributes
	----------
	commits : list[Commit]
	"""

	def __init__(self):
		self._commits = []

	def insert_commit(self, commit):
		"""
		Add
		Parameters
		----------
		commit : Commit
		"""



class SharedDocument:
	"""
	A document that handles simultaneous changes to it via a change log.
	TODO:: Perhaps figure out, how to use it for the GUI as well
	(would avoid duplication of code on client and server).
	"""

	def __init__(self):
		self.log = logging.getLogger("CT.SharedDocument")

		# List of lines.
		self.text = u""

		self.changelog = ChangeLog()

		self.unsaved_changes = True
		# TODO:: Should we have the same class on the client
		# side as well?

		# A random name for the document, if we ever were to try and save it.
		self.hash = cu.gen_random_string(32)
		self.local_filepath = "storage/{}.txt".format(self.hash)

	def insert(self, version, cursor, text):
		"""
		Insert text at a specific cursor position.
		"""
		self.text = self.text[:cursor] + text + self.text[cursor:]

	# TODO:: Return something for updating client cursors.

	def remove(self, version, cursor, length):
		"""
		Remove a selection of text at a specific cursor position.
		"""
		self.text = self.text[:cursor] + self.text[(cursor + length):]

	# TODO:: Return something for updating client cursors.

	def get_whole(self):
		"""
		Gets the whole text as a single string.
		"""
		return self.text

	def get_version(self):
		return 0

	def store(self):
		"""
		Stores the document in a file.
		"""
		try:
			if self.unsaved_changes:
				self.log.info("Writing to file..")
				with open(self.local_filepath, "wt") as f:
					text = self.get_whole()
					f.write(text)
		except Exception as e:
			self.log.exception(e)
