from PyQt5 import QtCore, QtGui, QtWidgets
from ctxt.client.ui_connect import Ui_ConnectDialog
from ctxt.client.ui_main import Ui_MainWindow
import ctxt.protocol as cp
import ctxt.util as cu

import logging

class ConnectDialog(QtWidgets.QDialog):
	"""
	Connection dialog.
	"""
	def __init__(self, parent, address, port, docname, nickname):
		super(ConnectDialog, self).__init__(parent)

		self.log = logging.getLogger("CT.Client.ConnectDlg")

		# pyuic5 ../../ui/connect.ui -o ui_connect.py
		# Loads the UI from the generated python file.
		self.content = Ui_ConnectDialog()
		self.content.setupUi(self)
		self.content.buttonBox.accepted.connect(self.do_connect)
		self.content.buttonBox.rejected.connect(self.do_cancel)

		self.content.editAddress.setText(address)
		self.content.editPort.setText(str(port))
		self.content.editName.setText(nickname)
		self.content.editDoc.setText(docname)

	def do_connect(self):
		"""
		The "Ok" handler.
		"""
		self.address = self.content.editAddress.text()
		self.port = int(self.content.editPort.text())
		self.nickname = self.content.editName.text()
		self.docname = self.content.editDoc.text()
	
	def do_cancel(self):
		"""
		The "Cancel" handler.
		"""
		self.address = None
		self.port = None
		self.nickname = None
		self.docname = None
	
	@staticmethod
	def ask_connection_info(parent, address, port, docname, nickname):
		"""
		Ask the user for connection parameters.
		The function arguments are taken as the default values.
		"""
		# Pop the modal dialog.
		dlg = ConnectDialog(parent, address, port, docname, nickname)
		result = dlg.exec_()
		# Fetch its results.
		return (result == QtWidgets.QDialog.Accepted, dlg.address, dlg.port, dlg.nickname, dlg.docname)

class MainWindow(QtWidgets.QMainWindow):
	"""
	The main window with the text editor.
	"""
	def __init__(self, client, address="localhost", port=7777, docname="test", nickname="Anon"):
		super(MainWindow, self).__init__()

		self.log = logging.getLogger("CT.Client.MainWnd")

		self.client = client
		self.update_interval = 0.1

		# pyrcc5 ../../ui/resources.qrc -o resources_rc.py
		# pyuic5 ../../ui/main.ui -o ui_main.py
		# Loads the UI from the generated python file.
		self.content = Ui_MainWindow()
		self.content.setupUi(self)
		self.content.actionConnect.triggered.connect(self.show_connect)
		# Install an event filter on the text box.
		self.content.textEdit.installEventFilter(self)
		# Though, disable the text editor until we've managed to join a document.
		self.content.textEdit.setDisabled(True)

		self.set_address(address)
		self.set_port(port)
		self.set_nickname(nickname)
		self.set_docname(docname)
		self.doc_ver = 0

		# Start the update timer
		self.update_timer = QtCore.QTimer()
		self.update_timer.setSingleShot(False)
		self.update_timer.timeout.connect(self.update)
		self.update_timer.start(self.update_interval)

		self.show()
	
	def set_address(self, address):
		"""
		Set server IP address or hostname.
		"""
		self.conn_address = address
	
	def set_port(self, port):
		"""
		Set server port to connect to.
		"""
		self.conn_port = int(port)
	
	def set_nickname(self, nickname):
		"""
		Set our nickname.
		"""
		self.nickname = nickname
	
	def set_docname(self, docname):
		"""
		Set the document name to join.
		"""
		if len(docname) < 1 or len(docname) > 128:
			self.docname = "test"
			self.log.error("Invalid document name \"{}\"".format(docname))
		else:
			self.docname = docname

	def show_connect(self):
		"""
		Handler for the "Connect" button.
		Shows a pop-up dialog for specifying
		connection parameters.
		"""
		conn = ConnectDialog.ask_connection_info(
				self, 
				self.conn_address, self.conn_port, 
				self.docname, self.nickname)
		if conn[0]:
			self.set_address(conn[1])
			self.set_port(conn[2])
			self.set_nickname(conn[3])
			self.set_docname(conn[4])

			self.do_connect()
	
	def do_connect(self):
		"""
		Connect to the server and join the document.
		"""
		if self.client.connect(self.conn_address, self.conn_port):
			self.client.join_doc(self.nickname, self.docname)
	
	def eventFilter(self, widget, event):
		"""
		Catch events in the text box.
		"""
		if event.type() == QtCore.QEvent.KeyPress and widget == self.content.textEdit:
			key = event.key()
			u = unicode(event.text())
			if key in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
				self.req_insert('\n')
			elif key == QtCore.Qt.Key_Backspace:
				# Support for Ctrl+Backspace (removes the previous word).
				if event.modifiers() & QtCore.Qt.ControlModifier:
					self.req_remove_word(-1)
				else:
					self.req_remove(-1)
			elif key == QtCore.Qt.Key_Delete:
				# Support for Ctrl+Delete (removes the next word).
				if event.modifiers() & QtCore.Qt.ControlModifier:
					self.req_remove_word(1)
				else:
					self.req_remove(1)
			elif key == QtCore.Qt.Key_Escape:
				self.close()
			elif cu.u_is_printable(u):
				self.req_insert(u)
		# Handle the rest
		return QtWidgets.QWidget.eventFilter(self, widget, event)

	def req_insert(self, text):
		"""
		Generate a text insertion request.
		"""
		cursor = self.content.textEdit.textCursor().position()
		d = {
				"op": cp.Protocol.REQ_INSERT,
				"version": self.doc_ver,
				"cursor": cursor,
				"text": text
				}
		self.client.send_text_change(d)
	
	def req_remove(self, length):
		"""
		Generate a text removal request.
		"""
		cursor = self.content.textEdit.textCursor().position()
		# We shouldn't send negative length to the server.
		# So, we'll remap the cursor position and length.
		if length < 0:
			length = abs(length)
			cursor -= length
		# And produce the message.
		d = {
				"op": cp.Protocol.REQ_REMOVE,
				"version": self.doc_ver,
				"cursor": cursor,
				"length": length
				}
		self.client.send_text_change(d)
	
	def req_remove_word(self, direction):
		"""
		Generate a request to remove a word
		relative to the cursor position.
		"""
		# Select the word left or right to the cursor.
		cursor = self.content.textEdit.textCursor()
		if direction > 0:
			cursor.movePosition(QtGui.QTextCursor.WordRight, QtGui.QTextCursor.KeepAnchor)
		else:
			cursor.movePosition(QtGui.QTextCursor.WordLeft, QtGui.QTextCursor.KeepAnchor)
		# Get selection length
		length = cursor.selectionEnd() - cursor.selectionStart()
		# And produce the message.
		d = {
				"op": cp.Protocol.REQ_REMOVE,
				"version": self.doc_ver,
				"cursor": cursor.selectionStart(),
				"length": length
				}
		self.client.send_text_change(d)

	def update(self):
		"""
		Check for any updates from the server,
		and schedule the next update.
		"""

		if not self.client.online:
			return

		self.client.update()

		if not self.client.queue_sc.empty():
			msg = self.client.queue_sc.get()
			# We've joined? Party?
			if msg.id == cp.Protocol.RES_OK and msg.req_id == cp.Protocol.REQ_JOIN:
				pass
			# We've received full text?
			elif msg.id == cp.Protocol.RES_TEXT:
				self.content.textEdit.setText(msg.text)
				# Enable the text editor
				self.content.textEdit.setDisabled(False)
			# Someone inserted some text?
			elif msg.id == cp.Protocol.RES_INSERT:
				self.log.debug(u"{} inserted version {} at {}: \"{}\"".format(
					msg.name, msg.version, msg.cursor, msg.text))
				# TODO:: Merging here

				# Generate a cursor at the desired position
				# and insert the text there.
				cursor = self.content.textEdit.textCursor()
				cursor.setPosition(msg.cursor)
				cursor.insertText(msg.text)
			# Someone removed some text?
			elif msg.id == cp.Protocol.RES_REMOVE:
				self.log.debug(u"{} spawned a new version {} with remove at {}-{}".format(
					msg.name, msg.version, msg.cursor, msg.length))
				# TODO:: Merging here

				# Generate the desired selection and remove the text.
				cursor = self.content.textEdit.textCursor()
				cursor.setPosition(msg.cursor)
				cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, msg.length)
				cursor.removeSelectedText()
	
	def closeEvent(self, event):
		"""
		Handler for the window close event.
		"""
		self.client.close()
