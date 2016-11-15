"""
Client thread class for the server.
"""

import ctxt.protocol as cp
import threading
import logging
import struct

class ClientThread(threading.Thread):
	STAT_STRANGER = 0
	STAT_EDITING = 1
	STAT_LEFT = 2

	def __init__(self):
		threading.Thread.__init__(self)
		self.log = logging.getLogger(Server.LOGNAME + ".Thread")

		self.online = False
		self.name = "Anon"
		self.state = ClientThread.STAT_STRANGER
	
	def run(self):
		self.online = True
		while self.online:
			try:
				hdr = self.socket.recv(cp.General.MIN_REQ_LEN)
				id, len = struct.unpack("<BI", hdr)

				if self.state == ClientThread.STAT_STRANGER:
					d = cp.User.unpack(hdr)
					print(d)

			except socket.timeout:
				pass
			except Exception as e:
				self.log.exception(e)

