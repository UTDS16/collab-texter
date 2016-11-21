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
		if not self.socket or not self.online:
			return

		self.online = True
		try:
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
	# Urwid color palette
	palette = [
			('body', 'default', 'default'),
			('status', 'default', 'default', 'bold'),
			('status-ok', 'light green', 'default', 'bold'),
			('status-nok', 'light red', 'default', 'bold'),
			]

	LOGNAME = "CT.Client.GUI"

	def __init__(self, address, port, name, update_period=0.2):
		self.log = logging.getLogger(GUI.LOGNAME)

		self.update_period = update_period

		self.client = Client()

		self.init_gui(address, port, name)
	
	def __del__(self):
		self.client.close()
	
	"""
	Initialize the subwindow for server connection.
	"""
	def init_gui_srv(self, address, port, name):
		self.e_srv_addr = urwid.Edit("Server address: ", address)
		self.ef_srv_addr = urwid.Filler(self.e_srv_addr)

		self.e_srv_port = urwid.IntEdit("Server port   : ", port)
		self.ef_srv_port = urwid.Filler(self.e_srv_port)

		self.e_nickname = urwid.Edit("Nickname      : ", name)
		self.ef_nickname = urwid.Filler(self.e_nickname)

		self.b_connect = urwid.Button("Connect")
		self.bf_connect = urwid.Filler(self.b_connect)

		self.b_exit = urwid.Button("Exit (esc)")
		self.bf_exit = urwid.Filler(self.b_exit)

		urwid.connect_signal(self.b_connect, "click", self.connect)
		urwid.connect_signal(self.b_exit, "click", self.stop)

		self.c_srv = urwid.Pile([
			self.ef_srv_addr, self.ef_srv_port, self.ef_nickname, 
			self.bf_connect, self.bf_exit])
		return self.c_srv

	"""
	Initialize the subwindow for some log messages.
	"""
	def init_gui_log(self):
		self.l_log = urwid.Text("Not connected")
		self.c_log = urwid.Filler(self.l_log)
		return self.c_log

	def init_gui_text(self):
		self.e_text = urwid.Edit()
		self.ef_text = urwid.Filler(self.e_text)
		self.f_text = urwid.SolidFill(' ')
		self.l_text = urwid.LineBox(self.f_text)
		self.c_text = urwid.Overlay(self.ef_text, self.l_text, "center", 1, "middle", 1)
		return self.c_text

	def init_gui(self, address, port, name):
		self.l_title = urwid.Text("Collaborative Text Editor Client")
		self.l_status = urwid.Text(("status-nok", "Not connected yet"))

		c_srv = self.init_gui_srv(address, port, name)
		c_log = self.init_gui_log()
		c_txt = self.init_gui_text()

		self.c_srv_log = urwid.Pile([
			("fixed", 5, c_srv),
			("weight", 70, c_log)
			])

		self.c_body = urwid.Columns([
			("weight", 70, c_txt), 
			("weight", 30, self.c_srv_log)
			])
		self.c_body.set_focus(1)

		self.c_frame = urwid.Frame(self.c_body, self.l_title, self.l_status)
	
	"""
	Handle unhandled keys.
	"""
	def key_handler(self, key):
		# All the keys to quit.
		if key in ('q', 'Q', 'x', 'X', "esc"):
			self.stop()
		return key

	"""
	Write a line into the log subwindow.
	"""
	def gui_log(self, message):
		self.l_log.set_text(self.l_log.text + "\n" + message)
		self.log.info(message)

	"""
	Set the status message in the footer.
	"""
	def gui_status(self, message):
		self.l_status.set_text(message)

	"""
	Connect to a server.
	"""
	def connect(self, button):
		address = self.e_srv_addr.edit_text
		port = int(self.e_srv_port.edit_text)
		self.gui_log("Connecting to {}:{}".format(address, port))

		if not self.client.connect(address, port):
			self.gui_log("Failed to connect")
		else:
			name = self.e_nickname.edit_text
			self.gui_log("Joining as {}".format(name))
			self.client.join_doc(name)

	"""
	Check for any updates from the server,
	and schedule the next update.
	"""
	def update(self, loop=None, user_data=None):
		self.client.update()
		self.loop.set_alarm_in(self.update_period, self.update)

	def start(self):
		self.loop = urwid.MainLoop(self.c_frame, palette=self.palette, unhandled_input=self.key_handler)
		self.loop.set_alarm_in(self.update_period, self.update)
		self.loop.run()

	"""
	Stop the client.
	"""
	def stop(self, button=None):
		self.log.info("Closing the shop")
		self.client.close()
		raise urwid.ExitMainLoop()

def init_logging():
	log = Client.get_log()
	log.setLevel(logging.DEBUG)

	handler = logging.FileHandler("log_client.txt")
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	# TODO:: Implement a handler for the GUI log window
	#handler = logging.StreamHandler()
	#handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	#log.addHandler(handler)

	return log

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Collaborative Text Editor Client")
	parser.add_argument('-a', '--address', dest='address', type=str, default="", help='server IP address')
	parser.add_argument('-p', '--port', dest='port', type=int, default=0, help='server port number')
	parser.add_argument('-n', '--name', dest='name', type=str, default="", help='nickname')

	args = parser.parse_args()

	log = init_logging()
	gui = GUI(args.address, args.port, args.name)
	try:
		gui.start()
	except urwid.main_loop.ExitMainLoop as e:
		pass
	except Exception as e:
		log.exception(e)
