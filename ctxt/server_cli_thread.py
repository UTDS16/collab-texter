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

	def __init__(self, socket, source, queue_cs):
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
		self.queue_cs = queue_cs
		# From Server to Client
		self.queue_sc = queue.Queue()

		self.cursor_pos = (0, 0)
	
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
				# Forward to the server
				msg = cp.Message(d, False)
				self.queue_cs.put(msg)

				# Some requests can be acknowledged right away.
				if msg.id == cp.Protocol.REQ_JOIN:
					self.name = msg.name
					self.state += 1
					# TODO:: Any auth?

					# Acknowledge the join.
					self.log.debug("Sending Ack")
					res = cp.Protocol.res_ok(msg.id)
					self.socket.sendall(res)

					# TODO:: Send the current version of the whole document.
				elif msg.id == cp.Protocol.REQ_SET_CURPOS:
					self.cursor_pos = msg.cursor

					# Acknowledge the request.
					self.log.debug("Sending Ack")
					res = cp.Protocol.res_ok(msg.id)
					self.socket.sendall(res)

				elif msg.id == cp.Protocol.REQ_INSERT:
					msg.cursor = self.cursor_pos

					# Acknowledge the request.
					self.log.debug("Sending Ack")
					res = cp.Protocol.res_ok(msg.id)
					self.socket.sendall(res)

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

