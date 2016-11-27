#!/usr/bin/python
import Queue as queue
import argparse
import errno
import logging
import signal
import socket

import ctxt.shared_document.document as cd
from ctxt.server.client_thread import ClientThread

import ctxt.protocol as cp
from ctxt.borg import Borg


class Server(Borg):
	"""
A server Borg, whatever that means. Ask Alex Martelli.
Anyways, it's a simpleton.
"""
	TCP_CLIENTS_QUEUE_LEN = 10
	LOGNAME = "CT.Server"

	@staticmethod
	def get_log():
		"""
	Get server log.
	"""
		return logging.getLogger(Server.LOGNAME)

	def __init__(self):
		Borg.__init__(self)

		self.log = Server.get_log()

		self.online = False
		self.socket = None
		# List of client threads with their source parameters.
		self.clients = []

		# A copy of the document that the clients are editing.
		self.document = cd.Document()
		# Queue for Client -> Server messages.
		self.queue_cs = queue.Queue()

	def listen(self, address='127.0.0.1', port=7777):
		"""
	Start listening for incoming connections.
	"""
		self.online = True

		# Create a TCP socket.
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Bind the socket to an address and port
		self.log.info("Binding socket to {}:{}".format(address, port))
		self.socket.bind((address, port))
		# Listen
		self.log.info("Listening for incoming connections..")
		self.socket.listen(Server.TCP_CLIENTS_QUEUE_LEN)
		# Non-blocking
		self.socket.setblocking(0)

		while self.online:
			try:
				# Separate threads for merging the document?
				while not self.queue_cs.empty():
					msg = self.queue_cs.get()

					# Request to insert some text?
					if msg.id == cp.Protocol.REQ_INSERT:
						# Update our copy of the document.
						self.document.insert(msg.version, msg.cursor, msg.text)
						# No longer a request. It's now a response.
						msg.id = cp.Protocol.RES_INSERT

						self.share_to_others(msg)
					# Request to remove some text?
					elif msg.id == cp.Protocol.REQ_REMOVE:
						self.document.remove(msg.version, msg.cursor, msg.length)
						msg.id = cp.Protocol.RES_REMOVE

						self.share_to_others(msg)
					# Request for the whole text?
					elif msg.id == cp.Protocol.REQ_TEXT:
						msg.id = cp.Protocol.RES_TEXT
						msg.text = self.document.get_whole()
						msg.version = self.document.get_version()

						self.send_to(msg)
				# New clients?
				client_socket, source = self.socket.accept()
				self.log.info("New client connected from {}".format(source))

				# Spawn a thread to serve the client.
				t = ClientThread(client_socket, source, self.queue_cs)
				t.start()
				self.clients.append([source, t])

			except socket.error as e:
				if e.errno not in [errno.EWOULDBLOCK]:
					self.log.exception(e)
			except Exception as e:
				if self.online:
					self.log.exception(e)

		# Close the socket, if any.
		if self.socket != None:
			self.log.info("Closing socket")
			self.socket.close()
		else:
			self.log.info("Socket already closed")

		# Join clients, if any.
		if len(self.clients) > 0:
			self.log.info("Joining threads")

			msg = cp.Message({"id": cp.Protocol.REQ_INT_CLOSE}, True)

			for client in self.clients:
				if len(client) == 2:
					t = client[1]
					self.log.info("Joining {}".format(client))
					t.queue_sc.put(msg)
					t.join()
		else:
			self.log.info("No client threads to join")

	def share_to_others(self, msg):
		"""
	Share a message to all others (except the author).
	"""
		# Propagate the message to other clients.
		for client in self.clients:
			if client != None and len(client) == 2:
				t = client[1]
				# Avoid forwarding messages to their author.
				if t.get_name() != msg.name:
					t.queue_sc.put(msg)

	def send_to(self, msg):
		"""
	Send a message to one specific client.
	"""
		# Send to a specific client.
		for client in self.clients:
			if client != None and len(client) == 2:
				t = client[1]
				if t.get_name() == msg.name:
					t.queue_sc.put(msg)
					return

	def close(self):
		"""
	Close the server on the next update.
	"""
		self.online = False


def init_logging():
	"""
Initialize logging.
"""
	log = logging.getLogger("CT")
	log.setLevel(logging.DEBUG)

	# Log to file.
	handler = logging.FileHandler("log_server.txt", encoding="UTF-8")
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)
	# And log to stdout.
	handler = logging.StreamHandler()
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	return log


def signal_handler(signum, frame):
	"""
Custom signal handler for SIGINT, SIGTERM.
"""
	# Reference the one and only Server.
	server = Server.get_instance()

	if signum == signal.SIGINT:
		server.log.warning("Received SIGINT, closing server..")
	elif signum == signal.SIGTERM:
		server.log.warning("Received SIGTERM, closing server..")

	# And close down the Server.
	server.online = False


def main():
	# Register signal handlers for SIGINT, SIGTERM.
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	parser = argparse.ArgumentParser(description="Collaborative Text Editor")
	parser.add_argument("--port", dest="port", type=int, default=7777, help="Port to listen on")

	args = parser.parse_args()

	log = init_logging()
	server = Server()
	server.listen(port=args.port)


if __name__ == '__main__':
	main()
