"""
Client thread class for the server.
"""

import ctxt.protocol as cp
import threading
import logging
import struct
import socket

class ClientThread(threading.Thread):
	LOGNAME = "CT.Server.Thread"

	STAT_STRANGER = 0
	STAT_EDITING = 1
	STAT_LEFT = 2

	def __init__(self, socket, source):
		threading.Thread.__init__(self)

		self.online = False
		self.name = "Anon"
		self.state = ClientThread.STAT_STRANGER

		self.socket = socket
		self.address = source[0]
		self.port = source[1]

		self.log = logging.getLogger(str(self))
	
	def __repr__(self):
		return ClientThread.LOGNAME + "({}, {})".format(self.address, self.port)
	
	def run(self):
		self.online = True
		while self.online:
			try:
				hdr = self.socket.recv(cp.General.MIN_REQ_LEN)
				if len(hdr) < 5:
					continue

				bid, blen = struct.unpack("<BI", hdr[:5])

				if self.state in [ClientThread.STAT_STRANGER, ClientThread.STAT_LEFT]:
					d = cp.User.unpack(hdr)
					print("User::" + d)
				elif self.state == ClientThread.STAT_EDITING:
					d = cp.Edit.unpack(hdr)
					print("Edit::" + d)
				else:
					self.log.error("Invalid state, {}".format(self.state))

			except socket.timeout:
				pass
			except Exception as e:
				# TODO:: Limit looped logs, somehow.
				self.log.exception(e)
		self.log.info("Closing socket")
		self.socket.close()

