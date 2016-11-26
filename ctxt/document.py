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
		self.lines = []

		self.unsaved_changes = True
		# TODO:: Should we have the same class on the client
		# side as well?

		# A random name for the document, if we ever were to try and save it.
		self.hash = cu.gen_random_string(32)
		self.local_filepath = "storage/{}.txt".format(self.hash)

	def insert(self, cursor, text):
		"""
	Insert text at a specific cursor position.
	"""
		(x, y) = cursor
		# Basically need to append to the text?
		if y > len(self.lines):
			self.log.warning("Cursor ({}, {}) and line number ({}) mismatch".format(x, y, len(self.lines)))
			y = len(self.lines)
		# This insertion is the first of its kind?
		if self.lines == [] or y == len(self.lines):
			line = ""
		else:
			line = self.lines[y]
		# Append to the line?
		if x > len(line):
			self.log.warning("Cursor ({}, {}) and line length ({}) mismatch".format(x, y, len(line)))
			x = len(line)

		# TODO:: Support for multiline insertions.

		if self.lines == [] or y == len(self.lines):
			self.lines.append(text)
		else:
			self.lines[y] = line[:x] + text + line[x:]

	def get_whole(self):
		"""
	Gets the whole text as a single string.
	"""
		return u'\n'.join(self.lines)

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
