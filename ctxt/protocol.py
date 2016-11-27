"""
Protocol classes with static methods to perform 
marshalling and unmarshalling.
"""

import struct
import ctxt.util as cu

"""
Request structure:
	REQ_ID (1 B)
	REQ_LEN (4 B)
	Arguments (REQ_LEN B)
"""

class Protocol():
	"""
Protocol for requests and responses.
"""
	# Minimum request length (header only)
	MIN_REQ_LEN = 5

	# Response: Request was okay
	RES_OK = 0x00
	# Response: Request was erroneous
	RES_ERROR = 0x01
	# Response: Text has been removed
	RES_REMOVE = 0x0D
	# Response: Text has been inserted
	RES_INSERT = 0x0E
	# Response: The text so far
	RES_TEXT = 0x0F

	# Request to join the active document
	REQ_JOIN = 0x21
	# Request to leave
	REQ_LEAVE = 0x22

	# Request for full text
	REQ_TEXT = 0xE0
	# Request to insert text
	REQ_INSERT = 0xE1
	# Request to set cursor position
	REQ_SET_CURPOS = 0xE3
	# Request to remove text
	REQ_REMOVE = 0xE4

	# Internal close request
	REQ_INT_CLOSE = 0xFF

	ERR_INVALID_DOCNAME = 0x01

	@staticmethod
	def res_ok(request_id):
		"""
		An "Okay" response to a specific request.
		"""
		return struct.pack("<BIB", Protocol.RES_OK, 1, request_id)

	@staticmethod
	def res_error(error):
		"""
		A "No way" response with an error code.
		"""
		return struct.pack(
				"<BII", Protocol.RES_ERROR, 
				4, error)
	
	@staticmethod
	def res_remove(name, version, cursor, length):
		"""
		Response "Author (name) just deleted (length) bytes from (cursor), in reference to (version)."
		"""
		bname = bytearray(name, "utf8")
		bnlen = len(bname)
		res = struct.pack(
				"<BIIIII{}s".format(bnlen),
				Protocol.RES_REMOVE,
				bnlen + 16, version, 
				cursor, length,
				bnlen, str(bname))
		return res
	
	@staticmethod
	def res_insert(name, version, cursor, text):
		"""
		Response "Author (name) just wrote (text) at (cursor), in reference to (version)."
		"""
		bname = bytearray(name, "utf8")
		bnlen = len(bname)
		btext = bytearray(text, "utf8")
		btlen = len(btext)
		res = struct.pack(
				"<BIIII{}sI{}s".format(bnlen, btlen),
				Protocol.RES_INSERT,
				bnlen + btlen + 16,
				version, cursor,
				bnlen, str(bname),
				btlen, str(btext))
		return res

	@staticmethod
	def res_text(version, cursor, text):
		"""
		Server says: "Here's thy doctrine"
		Full text response.
		"""
		btext = bytearray(text, "utf8")
		blen = len(btext)
		# TODO:: Should we have timestamp here, as well?
		# Or some kind of a commit hash?
		req = struct.pack(
				"<BIIII{}s".format(blen),
				Protocol.RES_TEXT,
				blen + 12, version, cursor,
				blen, str(btext))
		return req

	@staticmethod
	def req_join(name, doc):
		"""
		Join request from the client.
		"""
		bname = bytearray(name, "utf8")
		bnlen = len(bname)
		bdoc = bytearray(doc, "utf8")
		bdlen = len(bdoc)
		req = struct.pack(
				"<BII{}sI{}s".format(bnlen, bdlen),
				Protocol.REQ_JOIN,
				bnlen + bdlen + 8, 
				bnlen, str(bname),
				bdlen, str(bdoc))
		return req

	@staticmethod
	def req_leave():
		"""
		A leave request.
		"""
		req = struct.pack(
				"<BI", Protocol.REQ_LEAVE, 0)
		return req

	@staticmethod
	def req_insert(version, cursor, text):
		"""
		Request for an insertion of text on the remote.
		Client: "Help, I accidentally type (text)"
		"""
		btext = bytearray(text, "utf8")
		blen = len(btext)
		req = struct.pack(
				"<BIIII{}s".format(blen),
				Protocol.REQ_INSERT,
				blen + 12, version, cursor, 
				blen, str(btext))
		return req

	@staticmethod
	def req_remove(version, cursor, length):
		"""
		Request to remove text on the remote.
		"""
		req = struct.pack(
				"<BIIII",
				Protocol.REQ_REMOVE,
				12, version, 
				cursor, length)
		return req

	@staticmethod
	def req_set_cursor_pos(version, pos):
		"""
		Request for moving the current cursor position on the remote.
		"""
		req = struct.pack(
				"<BIII", 
				Protocol.REQ_SET_CURPOS,
				8, version, pos)
		return req

	@staticmethod
	def req_text():
		"""
		Request for the full text that is being edited by others.
		"""
		req = struct.pack(
				"<BI", 
				Protocol.REQ_TEXT, 
				0)
		return req

	@staticmethod
	def get_len(breq_original):
		"""
		Extract request length from request header binary.
		"""
		breq = bytearray(breq_original)
		r_id, r_len = struct.unpack("<BI", breq[:5])

		return r_len

	@staticmethod
	def unpack(breq_original):
		"""
		Extract request or response parameters from binary.
		"""
		breq = bytearray(breq_original)

		# Extract request ID and length.
		r_id, r_len = struct.unpack("<BI", breq[:5])
		breq = breq[5:(5+r_len)]
		# Create a dict of parameters.
		d = {"id":r_id}

		# Join
		if r_id == Protocol.REQ_JOIN:
			# Extract nickname
			bnlen, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			bname, = struct.unpack("<{}s".format(bnlen), breq[:bnlen])
			breq = breq[bnlen:]
			# Extract document name
			bdlen, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			bdoc, = struct.unpack("<{}s".format(bdlen), breq[:bdlen])

			d["name"] = bname.decode("utf-8")
			d["doc"] = bdoc.decode("utf-8")
		# Or leave?
		elif r_id == Protocol.REQ_LEAVE:
			# No arguments here.
			pass
		# A full text request?
		elif r_id == Protocol.REQ_TEXT:
			# No arguments
			pass
		elif r_id == Protocol.RES_TEXT:
			version, cursor, blen, btext = struct.unpack(
					"<III{}s".format(r_len - 12),
					breq)
			d["version"] = version
			d["cursor"] = cursor
			d["text"] = btext.decode("utf-8")
		# Insert text?
		elif r_id == Protocol.REQ_INSERT:
			version, cursor, blen, btext = struct.unpack(
					"<III{}s".format(r_len - 12),
					breq)
			d["version"] = version
			d["cursor"] = cursor
			d["text"] = btext.decode("utf-8")
		elif r_id == Protocol.RES_INSERT:
			# Version and cursor index
			version, cursor, = struct.unpack("<II", breq[:8])
			breq = breq[8:]
			# Extract author name
			bnlen, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			bname, = struct.unpack("<{}s".format(bnlen), breq[:bnlen])
			breq = breq[bnlen:]
			# Extract text
			btlen, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			btext, = struct.unpack("<{}s".format(btlen), breq)

			d["version"] = version
			d["cursor"] = cursor
			d["name"] = bname.decode("utf-8")
			d["text"] = btext.decode("utf-8")
		# Remove text?
		elif r_id == Protocol.REQ_REMOVE:
			version, cursor, length = struct.unpack(
					"<III", breq)
			d["version"] = version
			d["cursor"] = cursor
			d["length"] = length
		elif r_id == Protocol.RES_REMOVE:
			version, cursor, length, blen, bname = struct.unpack(
					"<IIII{}s".format(r_len - 16),
					breq)
			d["version"] = version
			d["cursor"] = cursor
			d["length"] = length
			d["name"] = bname.decode("utf-8")
		# Set remote cursor position?
		elif r_id == Protocol.REQ_SET_CURPOS:
			# Extract version and cursor index
			version, cursor = struct.unpack("<II", breq)
			d["version"] = version
			d["cursor"] = cursor
		elif r_id == Protocol.RES_OK:
			req, = struct.unpack("<B", breq[:1])
			d["req_id"] = req
		elif r_id == Protocol.RES_ERROR:
			error, = struct.unpack("<I", breq[:4])
			d["error"] = error
		return d

class Message():
	"""
	Class for describing the messages to be passed up & down the queues.
	"""
	def __init__(self, d, internal=False):
		self.__dict__ = d
		# An internal message (not propagated to authors)?
		self.internal = internal
