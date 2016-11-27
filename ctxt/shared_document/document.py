"""
Document class.
"""

import logging
import base64
import ctxt.util as cu

class Document:
	STORAGE_PATH = "storage/"

	"""
	A document class to handle insertions.
	TODO:: Perhaps figure out, how to use it for the GUI as well
	(would avoid duplication of code on client and server).
	"""
	def __init__(self, docname):
		self.log = logging.getLogger("CT.Document")

		self.docname = docname
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
		self.text = self.text[:cursor] + text + self.text[cursor:]
		self.store()

		# TODO:: Return something for updating client cursors.
	
	def remove(self, version, cursor, length):
		"""
		Remove a selection of text at a specific cursor position.
		"""
		self.text = self.text[:cursor] + self.text[(cursor+length):]
		self.store()

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

	def get_filepath(self):
		"""
		Produce a base64 filepath from document name.
		"""
		fname = base64.urlsafe_b64encode(self.docname)
		return os.path.join(Document.STORAGE_PATH, fname)

	def retrieve(self):
		"""
		Load the document.
		"""
		fpath = self.get_filepath()
		# Open the file for reading and create it if
		# it doesn't exist yet.
		with open(fpath, "a+") as fi:
			self.text = fi.read()

	@staticmethod
	def get_doc(self, docname):
		"""
		Gets a document by its name.
		If it doesn't exist, then it's created.
		"""
		doc = Document(docname)
		doc.retrieve()
		return doc

