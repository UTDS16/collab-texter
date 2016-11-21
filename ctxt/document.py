"""
Document class.
"""

import logging
import ctxt.util as cu

class Document:
	def __init__(self):
		self.log = logging.getLogger("CT.Document")
		self.lines = []
		self.unsaved_changes = True
		# TODO:: Should we have the same class on the client
		# side as well?
		self.hash = cu.gen_random_string(32)
		self.local_filepath = "storage/{}.txt".format(self.hash)

	"""
	Gets the whole text as a single string.
	"""
	def get_whole(self):
		return u'\n'.join(self.lines)

	"""
	Stores the document in a file.
	"""
	def store(self):
		try:
			if self.unsaved_changes:
				self.log.info("Writing to file..")
				with open(self.local_filepath, "wt") as f:
					text = self.get_whole()
					f.write(text)
		except Exception as e:
			self.log.exception(e)
