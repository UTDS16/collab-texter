#!/usr/bin/python

import ctxt.document as cd
from ctxt.borg import Borg
import ctxt.protocol as cp
import ctxt.util as cu
import socket
import argparse
import threading
import logging
import signal
import struct
import string
import urwid
import Queue as queue

"""
A client class for low-level production of requests and handling of responses.
"""
class Client():
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
		self.state = Client.STAT_IDLE
		self.queue_sc = queue.Queue()

		log.info("Starting the client")

	"""
	Connect to a server at a specific address and port.
	"""
	def connect(self, address="127.0.0.1", port=7777):
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

	"""
	Send a join request (with our nickname).
	"""
	def join_doc(self, name):
		self.state = Client.STAT_JOINING
		self.name = name

		req = cp.Protocol.req_join(name)
		self.socket.sendall(req)

	"""
	Check for messages waiting in socket buffer.
	"""
	def update(self):
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
			if e.errno not in [11]:
				self.log.exception(e)
		except Exception as e:
			self.log.exception(e)

	"""
	Confess to the great Server that we've sinned in
	letting the text change. The Server will handle this issue.
	"""
	def send_text_change(self, widget, change):
		x, y, op, text = change
		# It's an insert request?
		if op == cp.Protocol.REQ_INSERT:
			# Let's send cursor position first,
			req = cp.Protocol.req_set_cursor_pos(x, y)
			# then the text to be inserted there.
			req += cp.Protocol.req_insert(text)
			self.socket.sendall(req)
		# Nope, it's a plain cursor move?
		elif op == cp.Protocol.REQ_SET_CURPOS:
			req = cp.Protocol.req_set_cursor_pos(x, y)
			self.socket.sendall(req)
	
	"""
	Request for the whole text.
	Very useful in cases when the client has recovered from
	connection errors. Should call it then, I suppose.
	"""
	def get_whole_text(self):
		self.log.debug("Requesting for whole text")
		req = cp.Protocol.req_text()
		self.socket.sendall(req)

	"""
	Signal for the client to close on the next update.
	"""
	@staticmethod
	def close():
		Client.online = False

"""
A custom editor widget for multiline text editing.
It's based on a listbox with single line Edit widgets.
"""
class Editor(urwid.ListBox):
	# Name for logging.
	LOGNAME = "CT.Client.GUI.Editor"
	# Widget signals.
	signals = ["change"]

	def __init__(self):
		self.log = logging.getLogger(Editor.LOGNAME)

		self.lines = []
		self.insert_line()
		self.__super.__init__(self.lines)

	"""
	Insert a line at the cursor position.
	"""
	def insert_line(self, cursor=None):
		# Create a new editbox widget.
		edit = urwid.Edit()
		# This Edit is the first of its kind?
		if self.lines == []:
			self.lines.append(edit)
		else:
			if cursor == None:
				# Get current cursor position.
				(x, y) = self.get_pos()
			else:
				(x, y) = cursor

			self.log.info("Inserting line at {}, {}".format(x, y))
			# The line is to be inserted at the end of the text?
			if y == len(self.lines):
				self.lines.append(edit)
			else:
				# Cut the line from the cursor position.
				text = self.lines[y].get_text()[0]
				self.lines[y].set_edit_text(text[:x])
				edit.set_edit_text(text[x:])
				# Insert a new line.
				self.lines.insert(self.focus_position + 1, edit)
			# Focus on the fresh new line (even tho it's empty).
			self.focus_line(y + 1)
		# We might be interested in the signal. Let's register, just in case.
		urwid.connect_signal(edit, "change", self.text_changed)

	"""
	Remove a line at the cursor position.
	"""
	def remove_line(self, cursor=None, before=False, after=False):
		if len(self.lines) > 0:
			if cursor == None:
				# Get current cursor position.
				(x, y) = self.get_pos()
			else:
				(x, y) = cursor

			self.log.info("Removing line at {}, {}".format(x, y))

			# TODO:: Synchronizing, locking on the server.
			
			# Remove the line before.
			if before and y > 0:
				text = self.lines[y - 1].get_text()[0]
				text += self.lines[y].get_text()[0]
				self.lines[y - 1].set_edit_text(text)
				del self.lines[y]
			# Remove the line after.
			elif after and y < len(self.lines):
				text = self.lines[y].get_text()[0]
				text += self.lines[y + 1].get_text()[0]
				self.lines[y].set_edit_text(text)
				del self.lines[y + 1]
			self.focus_line(y)
	
	"""
	Insert a bunch of text at the cursor (defaults to current cursor).
	"""
	def insert_text(self, text, cursor=None):
		# No lines yet? Let's create one.
		if self.lines == []:
			self.insert_line(cursor)
		
		# No cursor position specified?
		if cursor == None:
			# Get current cursor position.
			(x, y) = self.get_pos()
		else:
			(x, y) = cursor

		# The text is to be inserted just
		# after the text?
		if y == len(self.lines):
			# Let's create a new line.
			self.insert_line(cursor)

		# Get the old line content.
		line = self.lines[y].get_text()[0]
		# Sandwich our text in between.
		line = line[:x] + text + line[x:]

		# TODO:: Add support for pasting multiline text.

		# Update the line.
		self.lines[y].set_edit_text(line)

	"""
	Set the whole text, to make sure it's up to date.
	"""
	def set_text(self, text):
		# TODO:: Merge?
		new_lines = text.split('\n')
		for i in range(0, len(new_lines)):
			# Append an empty line, if needed.
			if i >= len(self.lines):
				self.insert_line((0, i))
			self.log.debug(u"Setting line {} to \"{}\"".format(i, new_lines[i]))
			# Set its contents.
			self.lines[i].set_edit_text(new_lines[i])

	"""
	Text has changed.
	"""
	def text_changed(self, widget, line):
		# Keypress handler should be a better candidate for
		# updating the server about any changes, because
		# there we can have both the old as well as the new version of the active line.
		pass

	"""
	Focus on a specific line, or last line (-1).
	"""
	def focus_line(self, line_num=-1):
		if line_num < 0:
			self.set_focus(len(self.lines) - 1)
		else:
			self.set_focus(line_num)

	"""
	Get the current cursor position (x, y).
	"""
	def get_pos(self):
		# TODO:: Take unicode into account.

		y = self.focus_position
		# We don't know the number of columns.
		# So, I'll just supply a very large number.
		x, _ = self.lines[y].get_cursor_coords((1000000,))
		return (x, y)

	"""
	Handle unhandled keypresses.
	"""
	def keypress(self, size, key):
		# Remember the old cursor position.
		(x, y) = self.get_pos()
		# Have the superclass handle the key first.
		retval = self.__super.keypress(size, key)

		# The key wasn't handled?
		if retval:
			if key == "enter":
				self.insert_line()
				# Note that since resetting the cursor position
				# explicitly does not work, we'll simply simulate
				# a "Home" keypress.
				retval = self.__super.keypress(size, "home")
			elif key == "backspace":
				# BUG:: Need to set the new cursor position here, somehow.
				self.remove_line(before=True)
			elif key == "delete":
				self.remove_line(after=True)

		# Doesn't matter if the key was handled or not,
		# we'll bitch server about it.
		if cu.u_is_printable(key):
			self._emit("change", (x, y, cp.Protocol.REQ_INSERT, key))
			self.log.debug(u"Insert: ({}, {}): {}".format(x, y, key))
		# Keys that move the cursor.
		elif key in ["up", "down", "left", "right", "home", "end", "pageup", "pagedown"]:
			(nx, ny) = self.get_pos()
			self._emit("change", (nx, ny, cp.Protocol.REQ_SET_CURPOS, key))
			self.log.debug(u"Move: ({}, {}): ({}, {}): {}".format(x, y, nx, ny, key))

		return retval


"""
A graphical user interface class with urwid (!)
"""
class GUI():
	# Urwid color palette
	palette = [
			('body', 'default', 'default'),
			('status', 'default', 'default', 'bold'),
			('status-ok', 'light green', 'default', 'bold'),
			('status-nok', 'light red', 'default', 'bold'),
			]

	# Logname 
	LOGNAME = "CT.Client.GUI"

	def __init__(self, address, port, name, update_period=0.2):
		self.log = logging.getLogger(GUI.LOGNAME)

		# Period for update() callbacks.
		self.update_period = update_period

		self.client = Client()

		self.init_gui(address, port, name)
	
	def __del__(self):
		self.client.close()
	
	"""
	Initialize the subwindow for server connection.
	"""
	def init_gui_srv(self, address, port, name):
		# Note: Cannot pile plain widgets without vertical fillers.

		# Server address textbox.
		self.e_srv_addr = urwid.Edit("Server address: ", address)
		self.ef_srv_addr = urwid.Filler(self.e_srv_addr)
		# Server port editbox (integers only).
		self.e_srv_port = urwid.IntEdit("Server port   : ", port)
		self.ef_srv_port = urwid.Filler(self.e_srv_port)
		# Nickname textbox.
		self.e_nickname = urwid.Edit("Nickname      : ", name)
		self.ef_nickname = urwid.Filler(self.e_nickname)
		# Connect button.
		self.b_connect = urwid.Button("Connect")
		self.bf_connect = urwid.Filler(self.b_connect)
		# Exit button
		self.b_exit = urwid.Button("Exit (esc)")
		self.bf_exit = urwid.Filler(self.b_exit)
		# We want to know if someone clicked "Connect" or "Exit".
		urwid.connect_signal(self.b_connect, "click", self.connect)
		urwid.connect_signal(self.b_exit, "click", self.stop)
		# Pile the widgets on top of each-other.
		self.c_srv = urwid.Pile([
			self.ef_srv_addr, self.ef_srv_port, self.ef_nickname, 
			self.bf_connect, self.bf_exit])
		return self.c_srv

	"""
	Initialize the subwindow for some log messages.
	"""
	def init_gui_log(self):
		self.l_log = urwid.Text("Not connected")
		self.c_log = urwid.Filler(self.l_log, valign='top')
		return self.c_log

	"""
	Initialize the text editor subwindow.
	"""
	def init_gui_text(self):
		self.e_text = Editor()

		# Create a subwindow with an outlined box and the text editor on top of that.
		self.f_text = urwid.SolidFill(' ')
		self.l_text = urwid.LineBox(self.f_text)
		self.c_text = urwid.Overlay(
				self.e_text, self.l_text, 
				# Left alignment, 100% of the width
				"left", ("relative", 100), 
				# Top alignment, 100% of the height
				"top", ("relative", 100), 
				# 1 char margin, so we wouldn't overwrite the outline.
				left=1, right=1, top=1, bottom=1)

		# We deserve to know when the text changes.
		urwid.connect_signal(self.e_text, "change", self.client.send_text_change)

		return self.c_text

	"""
	Initialize the GUI with supplied values for the address, port and user nickname.
	"""
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
		self.focus_srv()

		self.c_frame = urwid.Frame(self.c_body, self.l_title, self.l_status)

	"""
	Focus on the connection subwindow.
	"""
	def focus_srv(self):
		self.c_body.set_focus(1)

	"""
	Focus on the text editor and a specific line in the editor (last line, by default).
	"""
	def focus_text(self, line_num=-1):
		self.c_body.set_focus(0)
		self.e_text.focus_line(line_num)
	
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
		# Take address and port number from the respective editboxes.
		address = self.e_srv_addr.edit_text
		port = int(self.e_srv_port.edit_text)
		# Try to connect.
		self.gui_log("Connecting to {}:{}".format(address, port))
		if not self.client.connect(address, port):
			self.gui_log("Failed to connect")
		else:
			self.gui_status(("status-ok", "Connected"))
			# Connected? Alright, let's try to join the active document.
			name = self.e_nickname.edit_text
			self.gui_log("Joining as {}".format(name))
			self.client.join_doc(name)

	"""
	Check for any updates from the server,
	and schedule the next update.
	"""
	def update(self, loop=None, user_data=None):
		self.client.update()

		if not self.client.queue_sc.empty():
			msg = self.client.queue_sc.get()
			# We've joined? Party?
			if msg.id == cp.Protocol.RES_OK and msg.req_id == cp.Protocol.REQ_JOIN:
				self.focus_text()
				self.gui_log("Joined")
				self.gui_status(("status-ok", "Editing"))
			# We've received full text?
			elif msg.id == cp.Protocol.RES_TEXT:
				self.e_text.set_text(msg.text)
			# Someone inserted some text?
			elif msg.id == cp.Protocol.RES_INSERT:
				(x, y) = msg.cursor
				self.log.debug(u"{} inserted at ({}, {}): \"{}\"".format(
					msg.name, x, y, msg.text))
				self.e_text.insert_text(msg.text, msg.cursor)


		self.loop.set_alarm_in(self.update_period, self.update)

	"""
	Start the main loop with an update callback issued at a period of self.update_period.
	"""
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

"""
Initialize logging for the application.
"""
def init_logging():
	log = logging.getLogger("CT")
	log.setLevel(logging.DEBUG)

	handler = logging.FileHandler("log_client.txt", encoding="UTF-8")
	handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	log.addHandler(handler)

	# TODO:: Implement a handler for the GUI log window
	#handler = logging.StreamHandler()
	#handler.setFormatter(logging.Formatter("[%(levelname)s: %(name)s]\t%(message)s"))
	#log.addHandler(handler)

	return log

"""
The Grand Main
"""
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
