"""
Document class.
"""

import logging

class Document:
	def __init__(self, hash):
		self.log = logging.getLogger("CT.Document")
		self.lines = []
		self.unsaved_changes = True
		# TODO:: Should we have the same class on the client
		# side as well?
		self.local_filepath = "storage/{}.txt".format(hash)

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
