"""
Document class.
"""

import logging
import ctxt.util as cu

class Document:
	"""
A document class to handle insertions.
TODO:: Perhaps figure out, how to use it for the GUI as well
(would avoid duplication of code on client and server).
"""
	def __init__(self):
		self.log = logging.getLogger("CT.Document")

		# List of lines.
		self.text = u""

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
		print "Cursor: {}".format(cursor)
		self.text = self.text[:cursor] + text + self.text[cursor:]

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
