"""
Document class.
"""

import logging
import base64
import os
import ctxt.protocol as cp
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
		self.active_commit = {}

		self.unsaved_changes = True
		# TODO:: Should we have the same class on the client
		# side as well?

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
	
	def process_commit(self, commit):
		print "Commit: {}".format(commit)
		for op in commit.sequence:
			if op["id"] == cp.Protocol.RES_INSERT:
				self.insert(commit.version, op["cursor"], op["text"])
			elif op["id"] == cp.Protocol.RES_REMOVE:
				self.remove(commit.version, op["cursor"], op["length"])
		self.active_commit = commit

	def update(self):
		"""
		Merge commits.
		"""
		commit = self.active_commit
		if commit == {}:
			return None
		self.active_commit = {}
		return commit

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
				with open(self.get_filepath(), "wt") as f:
					text = self.get_whole()
					f.write(text.encode("utf8"))
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
			self.text = fi.read().decode("utf8")

	def get_name(self):
		"""
		Get the name of the open document.
		"""
		return self.docname

	@staticmethod
	def get_doc(docname):
		"""
		Gets a document by its name.
		If it doesn't exist, then it's created.
		"""
		doc = Document(docname)
		doc.retrieve()
		return doc

