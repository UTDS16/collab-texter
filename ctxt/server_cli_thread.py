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
						if msg.id == cp.Protocol.REQ_JOIN:
							self.name = msg.name
							self.state += 1
						else:
							self.log.error("Please implement me")

				# Receive request header
				hdr = self.socket.recv(cp.Protocol.MIN_REQ_LEN)
				if len(hdr) < cp.Protocol.MIN_REQ_LEN:
					continue
				# Extract payload length
				r_len = cp.Protocol.get_len(hdr)
				# Receive request payload
				data = self.socket.recv(r_len)
				if len(data) < r_len:
					self.log.warning("Dropped request. Should increase timeout?")
					continue
				# Unpack the request
				d = cp.Protocol.unpack(hdr + data)
				self.log.debug("Request: {}".format(d))
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

