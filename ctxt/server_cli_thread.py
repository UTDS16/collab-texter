"""
Client thread class for the server.
"""

import ctxt.protocol as cp
import threading
import logging
import struct
import socket
import Queue as queue

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
						# Forward inserts.
						if msg.id == cp.Protocol.RES_INSERT:
							x, y = msg.cursor
							self.log.debug("Forwarding insert {}:({}, {}):{}".format(msg.name, x, y, msg.text))
							res = cp.Protocol.res_insert(msg.name, x, y, msg.text)
							self.socket.sendall(res)

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
				msg = cp.Message(d, False)

				# Some requests can be acknowledged right away.
				if msg.id == cp.Protocol.REQ_JOIN:
					self.name = msg.name
					self.state += 1
					# TODO:: Any auth?
					# TODO:: Send the current version of the whole document.

				elif msg.id == cp.Protocol.REQ_SET_CURPOS:
					self.cursor_pos = msg.cursor
					msg.name = self.name

				elif msg.id == cp.Protocol.REQ_INSERT:
					msg.cursor = self.cursor_pos
					msg.name = self.name

				# Forward to the server
				self.queue_cs.put(msg)

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

	def get_name(self):
		return self.name
