# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../../ui/connect.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConnectDialog(object):
    def setupUi(self, ConnectDialog):
        ConnectDialog.setObjectName("ConnectDialog")
        ConnectDialog.resize(349, 187)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConnectDialog)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(-1, 0, -1, -1)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(ConnectDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(ConnectDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.line = QtWidgets.QFrame(ConnectDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.line)
        self.label_3 = QtWidgets.QLabel(ConnectDialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(ConnectDialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.editAddress = QtWidgets.QLineEdit(ConnectDialog)
        self.editAddress.setObjectName("editAddress")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.editAddress)
        self.editName = QtWidgets.QLineEdit(ConnectDialog)
        self.editName.setObjectName("editName")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.editName)
        self.editPort = QtWidgets.QLineEdit(ConnectDialog)
        self.editPort.setObjectName("editPort")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.editPort)
        self.editDoc = QtWidgets.QLineEdit(ConnectDialog)
        self.editDoc.setObjectName("editDoc")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.editDoc)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConnectDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ConnectDialog)
        self.buttonBox.accepted.connect(ConnectDialog.accept)
        self.buttonBox.rejected.connect(ConnectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConnectDialog)

    def retranslateUi(self, ConnectDialog):
        _translate = QtCore.QCoreApplication.translate
        ConnectDialog.setWindowTitle(_translate("ConnectDialog", "Connect to server"))
        self.label.setText(_translate("ConnectDialog", "Server address:"))
        self.label_2.setText(_translate("ConnectDialog", "Server port:"))
        self.label_3.setText(_translate("ConnectDialog", "Your nickname:"))
        self.label_4.setText(_translate("ConnectDialog", "Document to join:"))
        self.editAddress.setText(_translate("ConnectDialog", "localhost"))
        self.editName.setText(_translate("ConnectDialog", "Anon"))
        self.editPort.setInputMask(_translate("ConnectDialog", "00000; "))
        self.editPort.setText(_translate("ConnectDialog", "7777"))

