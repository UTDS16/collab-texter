"""
Protocol classes with static methods to perform 
marshalling and unmarshalling.
"""

import struct

"""
Request structure:
	REQ_ID (1 B)
	REQ_LEN (4 B)
	Arguments (REQ_LEN B)
"""

class General:
	RES_OK = 0x00
	RES_ERROR = 0x01
	MIN_REQ_LEN = 5

	@staticmethod
	def res_ok():
		return struct.pack("<BI", General.RES_OK, 0)

	@staticmethod
	def res_error(error):
		return struct.pack(
				"<BII", General.RES_ERROR, 
				4, error)
	
	@staticmethod
	def unpack(breq):
		breq = bytearray(breq)
		r_id, r_len = struct.unpack("<BI", breq[:5])
		breq = breq[5:r_len]

		d = {"id":r_id}

		# Error?
		if r_id == General.RES_ERROR:
			error = struct.unpack("<I", breq)
			d["error"] = error
		return d

class User(General):
	REQ_JOIN = 0x21
	REQ_LEAVE = 0x22

	# TODO::
	@staticmethod
	def req_join(name):
		bname = bytearray(name)
		blen = len(bname)
		req = struct.pack(
				"<BII{}s".format(blen),
				User.REQ_JOIN,
				blen + 4, blen,
				bname)
		return req

	@staticmethod
	def req_leave():
		req = struct.pack(
				"<B", User.REQ_LEAVE)
		return req

	@staticmethod
	def unpack(breq_original):
		breq = bytearray(breq_original)
		r_id, r_len = struct.unpack("<BI", breq[:5])
		breq = breq[5:r_len]

		d = {"id":r_id}

		# Join
		if r_id == User.REQ_JOIN:
			blen, bname = struct.unpack(
					"<I{}s".format(r_len - 4),
					breq)
			d["name"] = unicode(b)
		# Or leave?
		elif r_id == User.REQ_LEAVE:
			# No arguments here.
			pass
		# Pass it to the superclass.
		else:
			return super(Edit, Edit).unpack(breq_original)
		return d

class Edit(General):
	REQ_INSERT = 0xE1
	REQ_GET_CURPOS = 0xE2
	REQ_SET_CURPOS = 0xE3

	@staticmethod
	def req_insert(text):
		btext = bytearray(text)
		blen = len(btext)
		req = struct.pack(
				"<BII{}s".format(blen),
				Edit.REQ_INSERT,
				blen + 4, blen,
				btext)
		return req

	@staticmethod
	def req_get_cursor_pos():
		req = struct.pack(
				"<BI",
				Edit.REQ_GET_CURPOS,
				0)
		return req

	@staticmethod
	def req_set_cursor_pos(x, y):
		req = struct.pack(
				"<BIII", 
				Edit.REQ_SET_CURPOS,
				8, x, y)
		return req

	@staticmethod
	def unpack(breq_original):
		breq = bytearray(breq_original)
		r_id, r_len = struct.unpack("<BI", breq[:5])
		breq = breq[5:r_len]

		d = {"id":r_id}

		# Insert text?
		if r_id == Edit.REQ_INSERT:
			blen, btext = struct.unpack(
					"<I{}s".format(r_len - 4),
					breq)
			d["text"] = unicode(btext)
		# Get remote cursor position?
		elif r_id == Edit.REQ_GET_CURPOS:
			pass
		# Set remote cursor position?
		elif r_id == Edit.REQ_SET_CURPOS:
			x, y = struct.unpack("<II", breq)
			d["cursor"] = (x, y)
		# Pass it to the superclass.
		else:
			return super(Edit, Edit).unpack(breq_original)
		return d
