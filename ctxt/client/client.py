#!/usr/bin/python
import Queue as queue
import argparse
import errno
import logging
import socket
import sys

from PyQt4 import QtCore, QtGui
from ctxt.client.ui import MainWindow

import ctxt.protocol as cp
import ctxt.util as cu

class Client():
	"""
	A client class for low-level production of requests and handling of responses.
	"""
	LOGNAME = "CT.Client"

	# Whether or not the client is supposed to be running.
	online = False

	STAT_IDLE = 0
	# Trying to connect.
	STAT_CONNECTING = 1
	# Server accepted the connection.
	STAT_CONNECTED = 2
	# Sent a join request, waiting for Ack.
	STAT_JOINING = 3
	# Server Acked our join request.
	STAT_JOINED = 4
	# We've received the full text, will edit it.
	STAT_EDITING = 5

	@staticmethod
	def get_log():
		"""
		Get client log.
		"""
		return logging.getLogger(Client.LOGNAME)

	def __init__(self):
		self.log = Client.get_log()

		Client.online = False
		self.socket = None
		self.state = Client.STAT_IDLE
		self.queue_sc = queue.Queue()

		self.log.info("Starting the client")

	def connect(self, address="127.0.0.1", port=7777):
		"""
		Connect to a server at a specific address and port.
		"""
		try:
			self.state = Client.STAT_CONNECTING

			# Create TCP/IP socket
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			if address == "localhost":
				address = "127.0.0.1"

			# We're running TCP connection from the GUI thread.
			# This makes implementation a bit easier.

			self.socket.connect((address, port))
			self.socket.setblocking(0)
			self.state = Client.STAT_CONNECTED
			self.online = True

			self.log.info("Connected to {}:{}".format(address, port))
		except Exception as e:
			self.log.exception("Failed to connect to {}:{} ".format(address, port))
			self.socket.close()
			self.socket = None
			return False
		return True

	def join_doc(self, nickname, doc):
		"""
		Send a join request (with our nickname).
		"""
		self.state = Client.STAT_JOINING
		self.nickname = nickname
		self.docname = doc

		# TODO:: Shouldn't convert from QString to string here.
		req = cp.Protocol.req_join(str(nickname), str(doc))
		self.socket.sendall(req)

	def update(self):
		"""
		Check for messages waiting in socket buffer.
		"""
		if not self.socket or not self.online:
			return
		if not self.online:
			self.log.info("Closing the connection")

			self.socket.close()
			self.socket = None
			return

		try:
			# Receive the header
			hdr = self.socket.recv(cp.Protocol.MIN_REQ_LEN)
			if len(hdr) < cp.Protocol.MIN_REQ_LEN:
				return

			self.log.debug("Received header: " + cu.to_hex_str(hdr))

			# TODO:: Should change socket back to blocking with timeout here?

			# Extract payload length.
			r_len = cp.Protocol.get_len(hdr)
			# Receive the rest of the data.
			#self.socket.setblocking(1)
			data = self.socket.recv(r_len)
			#self.socket.setblocking(0)
			if len(data) < r_len:
				self.log.warning("Dropped message")
				return

			self.log.debug("Received data: " + cu.to_hex_str(hdr + data))

			d = cp.Protocol.unpack(hdr + data)
			# Request acknowledged?
			if d["id"] == cp.Protocol.RES_OK:
				# That might mean we've successfully joined.
				if self.state == Client.STAT_JOINING and d["req_id"] == cp.Protocol.REQ_JOIN:
					self.log.info("We have successfully joined")

					self.state = Client.STAT_JOINED
					msg = cp.Message(d, True)
					self.queue_sc.put(msg)
					# Get the whole text that's written so far.
					self.get_whole_text()
			# Some kind of an error?
			elif d["id"] == cp.Protocol.RES_ERROR:
				self.log.error("Server error {}".format(d["error"]))
			# Someone inserted text?
			elif d["id"] == cp.Protocol.RES_INSERT:
				self.log.debug(d)
				if self.state == Client.STAT_EDITING:
					msg = cp.Message(d, True)
					self.queue_sc.put(msg)
			# We've received full text?
			elif d["id"] == cp.Protocol.RES_TEXT:
				self.log.debug(d)
				# We have full text, so we can go ahead and edit it.
				if self.state == Client.STAT_JOINED:
					self.state = Client.STAT_EDITING
				if self.state == Client.STAT_EDITING:
					msg = cp.Message(d, True)
					self.queue_sc.put(msg)
		except socket.error as e:
			# Skip "Resource temporarily unavailable".
			if e.errno not in [errno.EWOULDBLOCK]:
				self.log.exception(e)
		except Exception as e:
			self.log.exception(e)

	def send_text_change(self, change):
		"""
		Confess to the great Server that we've sinned in
		letting the text change. The Server will handle this issue.
		"""
		version, cursor, op, text = change
		# It's an insert request?
		if op == cp.Protocol.REQ_INSERT:
			req = cp.Protocol.req_insert(version, cursor, text)
			self.socket.sendall(req)
		# Nope, it's a plain cursor move?
		elif op == cp.Protocol.REQ_SET_CURPOS:
			req = cp.Protocol.req_set_cursor_pos(version, cursor)
			self.socket.sendall(req)
	
	def get_whole_text(self):
		"""
		Request for the whole text.
		Very useful in cases when the client has recovered from
		connection errors. Should call it then, I suppose.
		"""
		self.log.debug("Requesting for whole text")
		req = cp.Protocol.req_text()
		self.socket.sendall(req)

	@staticmethod
	def close():
		"""
		Signal for the client to close on the next update.
		"""
		Client.online = False

def init_logging():
	"""
	Initialize logging for the application.
	"""
	log = logging.getLogger("CT")
	log.setLevel(logging.DEBUG)

	handler = logging.FileHandler("log_client.txt", encoding="UTF-8")
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	return log

def main():
	parser = argparse.ArgumentParser(description="Collaborative Text Editor Client")
	parser.add_argument('-a', '--address', dest='address', type=str, default="", help='server IP address')
	parser.add_argument('-p', '--port', dest='port', type=int, default=0, help='server port number')
	parser.add_argument('-n', '--name', dest='name', type=str, default="", help='nickname')

	args = parser.parse_args()

	log = init_logging()

	try:
		app = QtGui.QApplication(sys.argv)
		client = Client()
		window = MainWindow(client)
		if args.address != "":
			window.set_address(args.address)
		if args.port != 0:
			window.set_port(args.port)
		if args.name != "":
			window.set_nickname(args.name)

		sys.exit(app.exec_())
	except Exception as e:
		log.exception(e)

"""
The Grand Main
"""
if __name__ == '__main__':
	main()
