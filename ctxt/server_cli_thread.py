"""
Client thread class for the server.
"""

import ctxt.protocol as cp
import threading
import logging
import struct
import socket
import queue

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
		self.socket.setblocking(0)
		self.address = source[0]
		self.port = source[1]

		self.log = logging.getLogger(str(self))

		# From Client to Server.
		self.queue_cs = queue.Queue()
		# From Server to Client
		self.queue_sc = queue.Queue()
	
	def __repr__(self):
		return ClientThread.LOGNAME + "({}, {})".format(self.address, self.port)
	
	def run(self):
		self.online = True
		while self.online:
			try:
				if not self.queue_sc.empty():
					msg = self.queue_sc.get()
					if msg.internal:
						if msg.id == cp.Protocol.REQ_INT_CLOSE:
							self.online = False
					else:
						self.log.error("Please implement me")

				hdr = self.socket.recv(cp.Protocol.MIN_REQ_LEN)
				if len(hdr) < 5:
					continue

				d = cp.Protocol.unpack(hdr)
				print("::" + d)
			except socket.timeout:
				pass
			except socket.error as e:
				if e.errno not in [11]:
					self.log.exception(e)
			except Exception as e:
				# TODO:: Limit looped logs, somehow.
				self.log.exception(e)
		self.log.info("Closing socket")
		self.socket.close()

