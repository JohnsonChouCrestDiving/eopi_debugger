# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_ble_command.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CR1_ble_command(object):
    def setupUi(self, CR1_ble_command):
        CR1_ble_command.setObjectName("CR1_ble_command")
        CR1_ble_command.resize(1500, 900)
        CR1_ble_command.setMinimumSize(QtCore.QSize(1500, 900))
        CR1_ble_command.setMaximumSize(QtCore.QSize(1500, 900))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        CR1_ble_command.setFont(font)
        self.display_textBrowser = QtWidgets.QTextBrowser(CR1_ble_command)
        self.display_textBrowser.setEnabled(True)
        self.display_textBrowser.setGeometry(QtCore.QRect(10, 280, 1400, 400))
        self.display_textBrowser.setMinimumSize(QtCore.QSize(1400, 400))
        self.display_textBrowser.setMaximumSize(QtCore.QSize(1400, 400))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.display_textBrowser.setFont(font)
        self.display_textBrowser.setObjectName("display_textBrowser")
        self.clear_uart_display_pushButton = QtWidgets.QPushButton(CR1_ble_command)
        self.clear_uart_display_pushButton.setEnabled(True)
        self.clear_uart_display_pushButton.setGeometry(QtCore.QRect(1030, 30, 100, 30))
        self.clear_uart_display_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.clear_uart_display_pushButton.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.clear_uart_display_pushButton.setFont(font)
        self.clear_uart_display_pushButton.setObjectName("clear_uart_display_pushButton")
        self.show_service_pushButton = QtWidgets.QPushButton(CR1_ble_command)
        self.show_service_pushButton.setEnabled(True)
        self.show_service_pushButton.setGeometry(QtCore.QRect(310, 130, 100, 30))
        self.show_service_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.show_service_pushButton.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.show_service_pushButton.setFont(font)
        self.show_service_pushButton.setObjectName("show_service_pushButton")
        self.show_characteristic_pushButton = QtWidgets.QPushButton(CR1_ble_command)
        self.show_characteristic_pushButton.setEnabled(True)
        self.show_characteristic_pushButton.setGeometry(QtCore.QRect(310, 80, 120, 30))
        self.show_characteristic_pushButton.setMinimumSize(QtCore.QSize(120, 30))
        self.show_characteristic_pushButton.setMaximumSize(QtCore.QSize(120, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.show_characteristic_pushButton.setFont(font)
        self.show_characteristic_pushButton.setObjectName("show_characteristic_pushButton")
        self.horizontalLayoutWidget = QtWidgets.QWidget(CR1_ble_command)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 20, 540, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scan_device_pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.scan_device_pushButton.setEnabled(True)
        self.scan_device_pushButton.setMinimumSize(QtCore.QSize(120, 30))
        self.scan_device_pushButton.setMaximumSize(QtCore.QSize(120, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.scan_device_pushButton.setFont(font)
        self.scan_device_pushButton.setObjectName("scan_device_pushButton")
        self.horizontalLayout.addWidget(self.scan_device_pushButton)
        self.ble_address_lineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.ble_address_lineEdit.setMinimumSize(QtCore.QSize(200, 0))
        self.ble_address_lineEdit.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.ble_address_lineEdit.setFont(font)
        self.ble_address_lineEdit.setObjectName("ble_address_lineEdit")
        self.horizontalLayout.addWidget(self.ble_address_lineEdit)
        self.connect_pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.connect_pushButton.setEnabled(True)
        self.connect_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.connect_pushButton.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.connect_pushButton.setFont(font)
        self.connect_pushButton.setObjectName("connect_pushButton")
        self.horizontalLayout.addWidget(self.connect_pushButton)
        self.disconnect_pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.disconnect_pushButton.setEnabled(True)
        self.disconnect_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.disconnect_pushButton.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.disconnect_pushButton.setFont(font)
        self.disconnect_pushButton.setObjectName("disconnect_pushButton")
        self.horizontalLayout.addWidget(self.disconnect_pushButton)

        self.retranslateUi(CR1_ble_command)
        QtCore.QMetaObject.connectSlotsByName(CR1_ble_command)

    def retranslateUi(self, CR1_ble_command):
        _translate = QtCore.QCoreApplication.translate
        CR1_ble_command.setWindowTitle(_translate("CR1_ble_command", "ble_command"))
        self.clear_uart_display_pushButton.setText(_translate("CR1_ble_command", "clear"))
        self.show_service_pushButton.setText(_translate("CR1_ble_command", "Show SVC"))
        self.show_characteristic_pushButton.setText(_translate("CR1_ble_command", "Show CHAR"))
        self.scan_device_pushButton.setText(_translate("CR1_ble_command", "Scan Device"))
        self.ble_address_lineEdit.setText(_translate("CR1_ble_command", "E8E92EEC9E8A"))
        self.connect_pushButton.setText(_translate("CR1_ble_command", "Connect"))
        self.disconnect_pushButton.setText(_translate("CR1_ble_command", "Disconnect"))
