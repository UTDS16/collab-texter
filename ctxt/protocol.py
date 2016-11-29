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
	# Response: Move text cursor
	RES_CURSOR = 0x0D
	# A commit, both a request as well as response (sequence of insert, remove operations)
	REQ_COMMIT = 0x0C
	RES_COMMIT = 0x0C
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

	# Internal close request
	REQ_INT_CLOSE = 0xFF

	# Invalid document name error
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
	def res_remove(name, cursor, length):
		"""
		Response "Author (name) just deleted (length) bytes from (cursor)."
		"""
		bname = bytearray(name, "utf8")
		bnlen = len(bname)
		res = struct.pack(
				"<BIII{}s".format(bnlen),
				Protocol.RES_REMOVE,
				bnlen + 8, 
				cursor, length,
				str(bname))
		return res
	
	@staticmethod
	def res_insert(name, cursor, text):
		"""
		Response "Author (name) just wrote (text) at (cursor)."
		"""
		bname = bytearray(name, "utf8")
		bnlen = len(bname)
		btext = bytearray(text, "utf8")
		btlen = len(btext)
		res = struct.pack(
				"<BIII{}s{}s".format(bnlen, btlen),
				Protocol.RES_INSERT,
				bnlen + btlen + 8,
				cursor,
				bnlen, str(bname), str(btext))
		return res

	@staticmethod
	def res_cursor(name, cursor):
		"""
		Response "Author (name) just moved to (cursor)."
		"""
		bname = bytearray(name, "utf8")
		bnlen = len(bname)
		res = struct.pack(
				"<BIII{}s".format(bnlen),
				Protocol.RES_INSERT,
				bnlen + 4,
				cursor,
				bnlen, str(bname))
		return res

	@staticmethod
	def res_commit(version, sequence):
		"""
		Commit response, consisting of a request or response sequence.
		"""
		# Build a binary of the operation sequence.
		bseq = bytearray()
		for op in sequence:
			op_id = op["id"]
			if op_id == Protocol.RES_INSERT:
				bseq += Protocol.res_insert(op["name"], op["cursor"], op["text"])
			elif op_id == Protocol.RES_REMOVE:
				bseq += Protocol.res_remove(op["name"], op["cursor"], op["length"])
			elif op_id == Protocol.RES_CURSOR:
				bseq += Protocol.res_cursor(op["name"], op["cursor"])
		bslen = len(bseq)
		
		res = struct.pack(
				"<BII{}s".format(bslen),
				Protocol.RES_COMMIT,
				bslen + 4, version, str(bseq))
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
				"<BIII{}s".format(blen),
				Protocol.RES_TEXT,
				blen + 8, version, cursor,
				str(btext))
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
				"<BII{}s{}s".format(bnlen, bdlen),
				Protocol.REQ_JOIN,
				bnlen + bdlen + 4, 
				bnlen, str(bname),
				str(bdoc))
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
	def unpack_op(breq):
		"""
		Unpack a text change operation.
		"""
		breq = bytearray(breq)

		# Extract request ID and length.
		r_id, r_len = struct.unpack("<BI", breq[:5])
		breq_rest = breq[(5+r_len):]
		breq = breq[5:(5+r_len)]
		# Create a dict of parameters.
		d = {"id":r_id}

		# Insert text?
		if r_id == Protocol.RES_INSERT:
			# Cursor index
			cursor, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			d["cursor"] = cursor
			# Extract author name
			bnlen, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			bname, = struct.unpack("<{}s".format(bnlen), breq[:bnlen])
			d["name"] = bname.decode("utf-8")
			# Extract text
			d["text"] = breq[bnlen:].decode("utf-8")
		# Remove text?
		elif r_id == Protocol.RES_REMOVE:
			# Extract cursor position, length.
			cursor, length = struct.unpack(
					"<II",	breq[:8])
			d["cursor"] = cursor
			d["length"] = length
			d["name"] = breq[8:].decode("utf-8")
		# Set cursor position?
		elif r_id == Protocol.RES_CURSOR:
			# Cursor index
			cursor, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			d["cursor"] = cursor
			# Extract author name
			bnlen, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			bname, = struct.unpack("<{}s".format(bnlen), breq[:bnlen])
			d["name"] = bname.decode("utf-8")

		return (breq_rest, d)

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
			d["name"] = bname.decode("utf-8")
			# Extract document name
			d["doc"] = breq[bnlen:].decode("utf-8")
		# Or leave?
		elif r_id == Protocol.REQ_LEAVE:
			# No arguments here.
			pass
		# A full text request?
		elif r_id == Protocol.REQ_TEXT:
			# No arguments
			pass
		elif r_id == Protocol.RES_TEXT:
			# Extract version, cursor
			version, cursor, = struct.unpack("<II", breq[:8])
			d["version"] = version
			d["cursor"] = cursor
			# Extract text
			d["text"] = breq[8:].decode("utf-8")
		# Commit?
		elif r_id == Protocol.RES_COMMIT:
			# Extract version
			version, = struct.unpack("<I", breq[:4])
			d["version"] = version
			d["sequence"] = []
			# Extract operations
			breq = breq[4:]
			while len(breq) > 0:
				breq, dop = Protocol.unpack_op(breq)
				d["sequence"].append(dop)
		# Ok response
		elif r_id == Protocol.RES_OK:
			req, = struct.unpack("<B", breq[:1])
			d["req_id"] = req
		# Error response
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
	
	def to_dict(self):
		"""
		Converts the message into a dictionary.
		"""
		return self.__dict__
