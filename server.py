#!/usr/bin/python3

import ctxt.document as cd
from ctxt.borg import Borg
from ctxt.server_cli_thread import ClientThread
import socket
import argparse
import threading
import logging
import signal
import struct


class Server(Borg):
	TCP_CLIENTS_QUEUE_LEN = 10
	LOGNAME = "CT.Server"

	"""
	Get server log.
	"""
	@staticmethod
	def get_log():
		return logging.getLogger(Server.LOGNAME)

	def __init__(self):
		Borg.__init__(self)

		self.log = Server.get_log()

		self.online = False
		self.socket = None
		self.clients = []

		log.info("Starting the server")

	"""
	Start listening for incoming connections.
	"""
	def listen(self, address='127.0.0.1', port=7777):
		self.online = True

		# Create a TCP socket.
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Bind the socket to an address and port
		self.log.info("Binding socket to {}:{}".format(address, port))
		self.socket.bind((address, port))
		# Listen
		self.log.info("Listening for incoming connections..")
		self.socket.listen(Server.TCP_CLIENTS_QUEUE_LEN)

		while self.online:
			try:
				client_socket, source = self.socket.accept()
				self.log.info("New client connected from {}".format(source))

				# Spawn a thread to serve the client.
				t = ClientThread(source[0], source[1])
				t.start()
				self.clients.append([source, t])
			except Exception as e:
				if self.online:
					self.log.exception(e)
	
	@staticmethod
	def close():
		self = Server.get_instance()
		
		self.online = False

def init_logging():
	log = Server.get_log()
	log.setLevel(logging.DEBUG)

	handler = logging.FileHandler("log_server.txt")
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	handler = logging.StreamHandler()
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	return log

"""
Custom signal handler for SIGINT, SIGTERM.
"""
def signal_handler(signum, frame):
	server = Server()

	if signum == signal.SIGINT:
		server.log.warning("Received SIGINT, closing server..")
	elif signum == signal.SIGTERM:
		server.log.warning("Received SIGTERM, closing server..")
	
	server.close()
	
if __name__ == '__main__':
	# Register signal handlers for SIGINT, SIGTERM.
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	parser = argparse.ArgumentParser(description="Collaborative Text Editor")
	parser.add_argument("--port", dest="port", type=int, default=7777, help="Port to listen on")

	args = parser.parse_args()

	log = init_logging()
	server = Server()
	server.listen(port = args.port)
