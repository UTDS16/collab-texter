# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../../ui/connect.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ConnectDialog(object):
    def setupUi(self, ConnectDialog):
        ConnectDialog.setObjectName(_fromUtf8("ConnectDialog"))
        ConnectDialog.resize(349, 187)
        self.verticalLayout = QtGui.QVBoxLayout(ConnectDialog)
        self.verticalLayout.setMargin(5)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setContentsMargins(-1, 0, -1, -1)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(ConnectDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(ConnectDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.line = QtGui.QFrame(ConnectDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.line)
        self.label_3 = QtGui.QLabel(ConnectDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtGui.QLabel(ConnectDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_4)
        self.editAddress = QtGui.QLineEdit(ConnectDialog)
        self.editAddress.setObjectName(_fromUtf8("editAddress"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.editAddress)
        self.editName = QtGui.QLineEdit(ConnectDialog)
        self.editName.setObjectName(_fromUtf8("editName"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.editName)
        self.editPort = QtGui.QLineEdit(ConnectDialog)
        self.editPort.setObjectName(_fromUtf8("editPort"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.editPort)
        self.editDoc = QtGui.QLineEdit(ConnectDialog)
        self.editDoc.setObjectName(_fromUtf8("editDoc"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.editDoc)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(ConnectDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ConnectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConnectDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConnectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConnectDialog)

    def retranslateUi(self, ConnectDialog):
        ConnectDialog.setWindowTitle(_translate("ConnectDialog", "Connect to server", None))
        self.label.setText(_translate("ConnectDialog", "Server address:", None))
        self.label_2.setText(_translate("ConnectDialog", "Server port:", None))
        self.label_3.setText(_translate("ConnectDialog", "Your nickname:", None))
        self.label_4.setText(_translate("ConnectDialog", "Document to join:", None))
        self.editAddress.setText(_translate("ConnectDialog", "localhost", None))
        self.editName.setText(_translate("ConnectDialog", "Anon", None))
        self.editPort.setInputMask(_translate("ConnectDialog", "00000; ", None))
        self.editPort.setText(_translate("ConnectDialog", "7777", None))

