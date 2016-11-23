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
	# Minimum request length (header only)
	MIN_REQ_LEN = 5

	# Response: Request was okay
	RES_OK = 0x00
	# Response: Request was erroneous
	RES_ERROR = 0x01
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
	# Request to get current cursor position
	REQ_GET_CURPOS = 0xE2
	# Request to set cursor position
	REQ_SET_CURPOS = 0xE3

	# Internal close request
	REQ_INT_CLOSE = 0xFF

	@staticmethod
	def res_ok(request_id):
		return struct.pack("<BIB", Protocol.RES_OK, 1, request_id)

	@staticmethod
	def res_error(error):
		return struct.pack(
				"<BII", Protocol.RES_ERROR, 
				4, error)
	
	@staticmethod
	def res_insert(name, x, y, text):
		bname = bytearray(name, "utf8")
		bnlen = len(bname)
		btext = bytearray(text, "utf8")
		btlen = len(btext)
		res = struct.pack(
				"<BIIII{}sI{}s".format(bnlen, btlen),
				Protocol.RES_INSERT,
				bnlen + btlen + 16,
				x, y,
				bnlen, str(bname),
				btlen, str(btext))
		return res

	@staticmethod
	def res_text(text):
		btext = bytearray(text, "utf8")
		blen = len(btext)
		req = struct.pack(
				"<BII{}s".format(blen),
				Protocol.REQ_TEXT,
				blen + 4, blen,
				str(btext))
		return req
	
	@staticmethod
	def req_join(name):
		bname = bytearray(name, "utf8")
		blen = len(bname)
		req = struct.pack(
				"<BII{}s".format(blen),
				Protocol.REQ_JOIN,
				blen + 4, blen,
				str(bname))
		return req

	@staticmethod
	def req_leave():
		req = struct.pack(
				"<B", Protocol.REQ_LEAVE)
		return req

	@staticmethod
	def req_insert(text):
		btext = bytearray(text, "utf8")
		blen = len(btext)
		req = struct.pack(
				"<BII{}s".format(blen),
				Protocol.REQ_INSERT,
				blen + 4, blen,
				str(btext))
		return req

	@staticmethod
	def req_get_cursor_pos():
		req = struct.pack(
				"<BI",
				Protocol.REQ_GET_CURPOS,
				0)
		return req

	@staticmethod
	def req_set_cursor_pos(x, y):
		req = struct.pack(
				"<BIII", 
				Protocol.REQ_SET_CURPOS,
				8, x, y)
		return req

	@staticmethod
	def get_len(breq_original):
		breq = bytearray(breq_original)
		r_id, r_len = struct.unpack("<BI", breq[:5])

		return r_len

	@staticmethod
	def unpack(breq_original):
		breq = bytearray(breq_original)

		r_id, r_len = struct.unpack("<BI", breq[:5])
		breq = breq[5:(5+r_len)]

		d = {"id":r_id}

		# Join
		if r_id == Protocol.REQ_JOIN:
			blen, bname = struct.unpack(
					"<I{}s".format(r_len - 4),
					breq)
			d["name"] = bname.decode("utf-8")
		# Or leave?
		elif r_id == Protocol.REQ_LEAVE:
			# No arguments here.
			pass
		# A full text request?
		elif r_id == Protocol.REQ_TEXT:
			# No arguments
			pass
		elif r_id == Protocol.RES_TEXT:
			blen, btext = struct.unpack(
					"<I{}s".format(r_len - 4),
					breq)
			d["text"] = bname.decode("utf-8")
		# Insert text?
		elif r_id == Protocol.REQ_INSERT:
			blen, btext = struct.unpack(
					"<I{}s".format(r_len - 4),
					breq)
			d["text"] = btext.decode("utf-8")
		elif r_id == Protocol.RES_INSERT:
			# Extract coordinates
			x, y, = struct.unpack("<II", breq[:8])
			breq = breq[8:]
			# Extract author name
			bnlen, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			bname, = struct.unpack("<{}s".format(bnlen), breq[:bnlen])
			breq = breq[bnlen:]
			# Extract text
			btlen, = struct.unpack("<I", breq[:4])
			breq = breq[4:]
			btext, = struct.unpack("<{}s".format(btlen), breq[:btlen])

			d["cursor"] = (x, y)
			d["name"] = bname.decode("utf-8")
			d["text"] = btext.decode("utf-8")
		# Get remote cursor position?
		elif r_id == Protocol.REQ_GET_CURPOS:
			pass
		# Set remote cursor position?
		elif r_id == Protocol.REQ_SET_CURPOS:
			x, y = struct.unpack("<II", breq)
			d["cursor"] = (x, y)
		elif r_id == Protocol.RES_OK:
			req, = struct.unpack("<B", breq[:1])
			d["req_id"] = req
		elif r_id == Protocol.RES_ERROR:
			error, = struct.unpack("<I", breq[:4])
			d["error"] = error
		return d

class Message():
	def __init__(self, d, internal=False):
		self.__dict__ = d
		self.internal = internal
