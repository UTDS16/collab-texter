#!/usr/bin/python3

import ctxt.document as cd
from ctxt.borg import Borg
import ctxt.protocol as cp
import socket
import argparse
import threading
import logging
import signal
import struct
import urwid

class Client():
	LOGNAME = "CT.Client"
	online = False

	"""
	Get client log.
	"""
	@staticmethod
	def get_log():
		return logging.getLogger(Client.LOGNAME)

	def __init__(self):
		self.log = Client.get_log()

		Client.online = False
		self.socket = None

		log.info("Starting the client")

	"""
	Connect to a server at a specific address and port.
	"""
	def connect(self, address="127.0.0.1", port=7777):
		try:
			# Create TCP/IP socket
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			if address == "localhost":
				address = "127.0.0.1"

			# We're running TCP connection from the GUI thread.
			# This way we can do away with queues only on 
			# the server side. Need non-blocking reads, tho.

			self.socket.connect((address, port))
			self.socket.setblocking(0)
			self.log.info("Connected to {}:{}".format(address, port))
		except Exception as e:
			self.log.exception("Failed to connect to {}:{} ".format(address, port))
			self.socket.close()
			self.socket = None
			return False
		return True

	def join_doc(self, name):
		self.name = name

		req = cp.Protocol.req_join(name)
		self.socket.sendall(req)

	"""
	Check for messages waiting in socket buffer.
	"""
	def update(self):
		if not self.socket:
			return

		Client.online = True
		try:
			while Client.online:
				# TODO:: Implement
				pass
		except socket.error as e:
			# Skip "Resource temporarily unavailable".
			if e.errno not in [11]:
				self.log.exception(e)
		except Exception as e:
			self.log.exception(e)
	
	@staticmethod
	def close():
		Client.online = False

class GUI():
	LOGNAME = "CT.Client.GUI"

	def __init__(self):
		self.log = logging.getLogger(GUI.LOGNAME)

		self.client = Client()

		self.log.error("Miroslav, please implement me!")
	
	def __del__(self):
		self.client.close()
	
	def start(self, address, port, name):
		if address != "" and port > 1024:
			self.client.connect(address, port)
		if name != "":
			self.name = name

		self.client.join_doc(self.name)

		self.log.error("Miroslav, please implement me!")

def init_logging():
	log = Client.get_log()
	log.setLevel(logging.DEBUG)

	handler = logging.FileHandler("log_client.txt")
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	handler = logging.StreamHandler()
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	return log

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Collaborative Text Editor Client")
	parser.add_argument('-a', '--address', dest='address', type=str, default="", help='server IP address')
	parser.add_argument('-p', '--port', dest='port', type=int, default=0, help='server port number')
	parser.add_argument('-n', '--name', dest='name', type=str, default="", help='nickname')

	args = parser.parse_args()

	log = init_logging()
	gui = GUI()
	try:
		gui.start(args.address, args.port, args.name)
	except urwid.main_loop.ExitMainLoop as e:
		pass
	except Exception as e:
		log.exception(e)
