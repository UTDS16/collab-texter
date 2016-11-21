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
	RES_OK = 0x00
	RES_ERROR = 0x01
	MIN_REQ_LEN = 5

	REQ_JOIN = 0x21
	REQ_LEAVE = 0x22

	REQ_INSERT = 0xE1
	REQ_GET_CURPOS = 0xE2
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
	def req_join(name):
		bname = bytearray(name, "utf8")
		blen = len(bname)
		req = struct.pack(
				"<BII{}s".format(blen),
				Protocol.REQ_JOIN,
				blen + 4, blen,
				bname)
		return req

	@staticmethod
	def req_leave():
		req = struct.pack(
				"<B", Protocol.REQ_LEAVE)
		return req

	@staticmethod
	def req_insert(text):
		btext = bytearray(text)
		blen = len(btext)
		req = struct.pack(
				"<BII{}s".format(blen),
				Protocol.REQ_INSERT,
				blen + 4, blen,
				btext)
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
		# Insert text?
		elif r_id == Protocol.REQ_INSERT:
			blen, btext = struct.unpack(
					"<I{}s".format(r_len - 4),
					breq)
			d["text"] = btext.decode("utf-8")
		# Get remote cursor position?
		elif r_id == Protocol.REQ_GET_CURPOS:
			pass
		# Set remote cursor position?
		elif r_id == Protocol.REQ_SET_CURPOS:
			x, y = struct.unpack("<II", breq)
			d["cursor"] = (x, y)
		elif r_id == Protocol.RES_OK:
			req, = struct.unpack("<B", breq)
			d["req_id"] = req
		elif r_id == Protocol.RES_ERROR:
			error, = struct.unpack("<I", breq)
			d["error"] = error
		return d

class Message():
	def __init__(self, d, internal=False):
		self.__dict__ = d
		self.internal = internal
