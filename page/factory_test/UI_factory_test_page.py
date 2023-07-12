# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_factory_test_page.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_factory_test_func(object):
    def setupUi(self, factory_test_func):
        factory_test_func.setObjectName("factory_test_func")
        factory_test_func.resize(1500, 900)
        factory_test_func.setMinimumSize(QtCore.QSize(1500, 900))
        factory_test_func.setMaximumSize(QtCore.QSize(1500, 900))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(11)
        factory_test_func.setFont(font)
        factory_test_func.setAutoFillBackground(False)
        factory_test_func.setStyleSheet("")
        factory_test_func.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.gBox_DevManager = QtWidgets.QGroupBox(factory_test_func)
        self.gBox_DevManager.setGeometry(QtCore.QRect(60, 20, 611, 581))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        font.setItalic(True)
        font.setStrikeOut(False)
        self.gBox_DevManager.setFont(font)
        self.gBox_DevManager.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.gBox_DevManager.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.gBox_DevManager.setCheckable(False)
        self.gBox_DevManager.setObjectName("gBox_DevManager")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.gBox_DevManager)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 30, 567, 541))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.VLayout_devManage = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.VLayout_devManage.setContentsMargins(0, 0, 0, 0)
        self.VLayout_devManage.setObjectName("VLayout_devManage")
        self.HLayout_currDev = QtWidgets.QHBoxLayout()
        self.HLayout_currDev.setContentsMargins(-1, 0, -1, -1)
        self.HLayout_currDev.setObjectName("HLayout_currDev")
        self.label_currentDevice = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_currentDevice.setFont(font)
        self.label_currentDevice.setObjectName("label_currentDevice")
        self.HLayout_currDev.addWidget(self.label_currentDevice)
        self.label_currDevAddr = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(20)
        font.setItalic(False)
        self.label_currDevAddr.setFont(font)
        self.label_currDevAddr.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.label_currDevAddr.setObjectName("label_currDevAddr")
        self.HLayout_currDev.addWidget(self.label_currDevAddr)
        self.Btn_findWatch = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        self.Btn_findWatch.setFont(font)
        self.Btn_findWatch.setObjectName("Btn_findWatch")
        self.HLayout_currDev.addWidget(self.Btn_findWatch)
        self.HLayout_currDev.setStretch(1, 5)
        self.VLayout_devManage.addLayout(self.HLayout_currDev)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.HLayout_fwVer = QtWidgets.QHBoxLayout()
        self.HLayout_fwVer.setContentsMargins(-1, 0, -1, -1)
        self.HLayout_fwVer.setObjectName("HLayout_fwVer")
        self.label_fwVer = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_fwVer.setFont(font)
        self.label_fwVer.setObjectName("label_fwVer")
        self.HLayout_fwVer.addWidget(self.label_fwVer)
        self.label_currFwVer = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(20)
        self.label_currFwVer.setFont(font)
        self.label_currFwVer.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.label_currFwVer.setObjectName("label_currFwVer")
        self.HLayout_fwVer.addWidget(self.label_currFwVer)
        self.HLayout_fwVer.setStretch(1, 1)
        self.horizontalLayout.addLayout(self.HLayout_fwVer)
        self.HLayout_fwTime = QtWidgets.QHBoxLayout()
        self.HLayout_fwTime.setContentsMargins(-1, 0, -1, -1)
        self.HLayout_fwTime.setObjectName("HLayout_fwTime")
        self.label_fwTime = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_fwTime.setFont(font)
        self.label_fwTime.setObjectName("label_fwTime")
        self.HLayout_fwTime.addWidget(self.label_fwTime)
        self.label_currFwTime = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(20)
        self.label_currFwTime.setFont(font)
        self.label_currFwTime.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.label_currFwTime.setObjectName("label_currFwTime")
        self.HLayout_fwTime.addWidget(self.label_currFwTime)
        self.HLayout_fwTime.setStretch(1, 5)
        self.horizontalLayout.addLayout(self.HLayout_fwTime)
        self.horizontalLayout.setStretch(0, 9)
        self.horizontalLayout.setStretch(1, 10)
        self.VLayout_devManage.addLayout(self.horizontalLayout)
        self.Btn_connect = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(22)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.Btn_connect.setFont(font)
        self.Btn_connect.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Btn_connect.setObjectName("Btn_connect")
        self.VLayout_devManage.addWidget(self.Btn_connect)
        self.label_nearbyBtDev = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        font.setItalic(False)
        self.label_nearbyBtDev.setFont(font)
        self.label_nearbyBtDev.setObjectName("label_nearbyBtDev")
        self.VLayout_devManage.addWidget(self.label_nearbyBtDev)
        self.listWidget_deviceList = QtWidgets.QListWidget(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.listWidget_deviceList.setFont(font)
        self.listWidget_deviceList.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.listWidget_deviceList.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.listWidget_deviceList.setObjectName("listWidget_deviceList")
        self.VLayout_devManage.addWidget(self.listWidget_deviceList)
        self.Btn_scanDevice = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(22)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.Btn_scanDevice.setFont(font)
        self.Btn_scanDevice.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Btn_scanDevice.setObjectName("Btn_scanDevice")
        self.VLayout_devManage.addWidget(self.Btn_scanDevice)
        self.VLayout_devManage.setStretch(0, 10)
        self.VLayout_devManage.setStretch(4, 100)
        self.gBox_guiMesg = QtWidgets.QGroupBox(factory_test_func)
        self.gBox_guiMesg.setGeometry(QtCore.QRect(60, 630, 1381, 211))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        font.setItalic(True)
        self.gBox_guiMesg.setFont(font)
        self.gBox_guiMesg.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.gBox_guiMesg.setObjectName("gBox_guiMesg")
        self.textBrowser_guiMessage = QtWidgets.QTextBrowser(self.gBox_guiMesg)
        self.textBrowser_guiMessage.setGeometry(QtCore.QRect(10, 30, 1361, 171))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        font.setItalic(False)
        self.textBrowser_guiMessage.setFont(font)
        self.textBrowser_guiMessage.setStyleSheet("")
        self.textBrowser_guiMessage.setObjectName("textBrowser_guiMessage")
        self.gBox_fwUpdate = QtWidgets.QGroupBox(factory_test_func)
        self.gBox_fwUpdate.setGeometry(QtCore.QRect(810, 20, 631, 101))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        font.setItalic(True)
        self.gBox_fwUpdate.setFont(font)
        self.gBox_fwUpdate.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.gBox_fwUpdate.setObjectName("gBox_fwUpdate")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.gBox_fwUpdate)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(20, 30, 591, 61))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.Layout_fwOtaUpdata = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.Layout_fwOtaUpdata.setContentsMargins(0, 0, 0, 0)
        self.Layout_fwOtaUpdata.setObjectName("Layout_fwOtaUpdata")
        self.Btn_selectFile = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.Btn_selectFile.setMinimumSize(QtCore.QSize(0, 16))
        self.Btn_selectFile.setMaximumSize(QtCore.QSize(16777215, 80))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.Btn_selectFile.setFont(font)
        self.Btn_selectFile.setObjectName("Btn_selectFile")
        self.Layout_fwOtaUpdata.addWidget(self.Btn_selectFile)
        self.textEdit_filePath = QtWidgets.QTextEdit(self.horizontalLayoutWidget_2)
        self.textEdit_filePath.setMinimumSize(QtCore.QSize(0, 50))
        self.textEdit_filePath.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        font.setItalic(False)
        self.textEdit_filePath.setFont(font)
        self.textEdit_filePath.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.textEdit_filePath.setObjectName("textEdit_filePath")
        self.Layout_fwOtaUpdata.addWidget(self.textEdit_filePath)
        self.Btn_updataFw = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.Btn_updataFw.setMaximumSize(QtCore.QSize(16777215, 80))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.Btn_updataFw.setFont(font)
        self.Btn_updataFw.setObjectName("Btn_updataFw")
        self.Layout_fwOtaUpdata.addWidget(self.Btn_updataFw)
        self.gBox_calBaro = QtWidgets.QGroupBox(factory_test_func)
        self.gBox_calBaro.setGeometry(QtCore.QRect(810, 230, 631, 91))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        font.setItalic(True)
        self.gBox_calBaro.setFont(font)
        self.gBox_calBaro.setAutoFillBackground(False)
        self.gBox_calBaro.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.gBox_calBaro.setObjectName("gBox_calBaro")
        self.Btn_Calibrate = QtWidgets.QPushButton(self.gBox_calBaro)
        self.Btn_Calibrate.setGeometry(QtCore.QRect(290, 30, 321, 51))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.Btn_Calibrate.setFont(font)
        self.Btn_Calibrate.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Btn_Calibrate.setStyleSheet("")
        self.Btn_Calibrate.setObjectName("Btn_Calibrate")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.gBox_calBaro)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 30, 251, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.HLayout_inputCOMport = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.HLayout_inputCOMport.setContentsMargins(0, 0, 0, 0)
        self.HLayout_inputCOMport.setObjectName("HLayout_inputCOMport")
        self.label_COM = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        font.setItalic(False)
        self.label_COM.setFont(font)
        self.label_COM.setObjectName("label_COM")
        self.HLayout_inputCOMport.addWidget(self.label_COM)
        self.lineEdit_COMport = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_COMport.setMinimumSize(QtCore.QSize(0, 46))
        self.lineEdit_COMport.setMaximumSize(QtCore.QSize(16777215, 46))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        self.lineEdit_COMport.setFont(font)
        self.lineEdit_COMport.setAutoFillBackground(False)
        self.lineEdit_COMport.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEdit_COMport.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.lineEdit_COMport.setText("")
        self.lineEdit_COMport.setPlaceholderText("")
        self.lineEdit_COMport.setObjectName("lineEdit_COMport")
        self.HLayout_inputCOMport.addWidget(self.lineEdit_COMport)
        self.Btn_COMportOpen = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.Btn_COMportOpen.setMinimumSize(QtCore.QSize(0, 46))
        self.Btn_COMportOpen.setMaximumSize(QtCore.QSize(16777215, 46))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        font.setItalic(False)
        self.Btn_COMportOpen.setFont(font)
        self.Btn_COMportOpen.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Btn_COMportOpen.setObjectName("Btn_COMportOpen")
        self.HLayout_inputCOMport.addWidget(self.Btn_COMportOpen)
        self.HLayout_inputCOMport.setStretch(2, 2)
        self.gBox_DevTest = QtWidgets.QGroupBox(factory_test_func)
        self.gBox_DevTest.setGeometry(QtCore.QRect(810, 340, 631, 261))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        font.setItalic(True)
        self.gBox_DevTest.setFont(font)
        self.gBox_DevTest.setAutoFillBackground(False)
        self.gBox_DevTest.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.gBox_DevTest.setFlat(False)
        self.gBox_DevTest.setObjectName("gBox_DevTest")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.gBox_DevTest)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(24, 30, 591, 221))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.VLayout_devTest = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.VLayout_devTest.setContentsMargins(0, 0, 0, 0)
        self.VLayout_devTest.setObjectName("VLayout_devTest")
        self.Btn_devTest = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.Btn_devTest.setFont(font)
        self.Btn_devTest.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Btn_devTest.setObjectName("Btn_devTest")
        self.VLayout_devTest.addWidget(self.Btn_devTest)
        self.label_testDevHistory = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        font.setItalic(False)
        self.label_testDevHistory.setFont(font)
        self.label_testDevHistory.setObjectName("label_testDevHistory")
        self.VLayout_devTest.addWidget(self.label_testDevHistory)
        self.textBrowser_testHistory = QtWidgets.QTextBrowser(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        self.textBrowser_testHistory.setFont(font)
        self.textBrowser_testHistory.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.textBrowser_testHistory.setObjectName("textBrowser_testHistory")
        self.VLayout_devTest.addWidget(self.textBrowser_testHistory)
        self.gBox_DevSn = QtWidgets.QGroupBox(factory_test_func)
        self.gBox_DevSn.setGeometry(QtCore.QRect(810, 140, 631, 71))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        font.setItalic(True)
        self.gBox_DevSn.setFont(font)
        self.gBox_DevSn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.gBox_DevSn.setObjectName("gBox_DevSn")
        self.lineEdit_DevSN = QtWidgets.QLineEdit(self.gBox_DevSn)
        self.lineEdit_DevSN.setGeometry(QtCore.QRect(50, 30, 561, 30))
        self.lineEdit_DevSN.setMinimumSize(QtCore.QSize(0, 30))
        self.lineEdit_DevSN.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        self.lineEdit_DevSN.setFont(font)
        self.lineEdit_DevSN.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEdit_DevSN.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_DevSN.setText("")
        self.lineEdit_DevSN.setMaxLength(32)
        self.lineEdit_DevSN.setDragEnabled(True)
        self.lineEdit_DevSN.setClearButtonEnabled(True)
        self.lineEdit_DevSN.setObjectName("lineEdit_DevSN")

        self.retranslateUi(factory_test_func)
        QtCore.QMetaObject.connectSlotsByName(factory_test_func)

    def retranslateUi(self, factory_test_func):
        _translate = QtCore.QCoreApplication.translate
        factory_test_func.setWindowTitle(_translate("factory_test_func", "factory test function"))
        self.gBox_DevManager.setTitle(_translate("factory_test_func", "Device Manage"))
        self.label_currentDevice.setText(_translate("factory_test_func", "Current Device:"))
        self.label_currDevAddr.setText(_translate("factory_test_func", "N/A"))
        self.Btn_findWatch.setText(_translate("factory_test_func", "Find"))
        self.label_fwVer.setText(_translate("factory_test_func", "Fw ver."))
        self.label_currFwVer.setText(_translate("factory_test_func", "N/A"))
        self.label_fwTime.setText(_translate("factory_test_func", "Fw time:"))
        self.label_currFwTime.setText(_translate("factory_test_func", "N/A"))
        self.Btn_connect.setText(_translate("factory_test_func", "CONNECT >>"))
        self.label_nearbyBtDev.setText(_translate("factory_test_func", "Nearby bluetooth device:"))
        self.Btn_scanDevice.setText(_translate("factory_test_func", "SCAN DEVICE"))
        self.gBox_guiMesg.setTitle(_translate("factory_test_func", "GUI Message"))
        self.gBox_fwUpdate.setTitle(_translate("factory_test_func", "Device F.W. Update:"))
        self.Btn_selectFile.setText(_translate("factory_test_func", "select file"))
        self.Btn_updataFw.setText(_translate("factory_test_func", "update FW"))
        self.gBox_calBaro.setTitle(_translate("factory_test_func", "GroupBox"))
        self.Btn_Calibrate.setText(_translate("factory_test_func", " Calibrate >>"))
        self.label_COM.setText(_translate("factory_test_func", "C O M"))
        self.Btn_COMportOpen.setText(_translate("factory_test_func", "Open"))
        self.gBox_DevTest.setTitle(_translate("factory_test_func", "Device Test"))
        self.Btn_devTest.setText(_translate("factory_test_func", "<<  COMPREHENSIVE TEST  >>"))
        self.label_testDevHistory.setText(_translate("factory_test_func", "Test devices history:"))
        self.gBox_DevSn.setTitle(_translate("factory_test_func", "Device SN"))
        self.lineEdit_DevSN.setPlaceholderText(_translate("factory_test_func", "Please enter serial number..."))
