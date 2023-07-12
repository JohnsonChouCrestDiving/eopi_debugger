#standard library
import sys
import os
import base64
import asyncio
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from asyncqt import QEventLoop, asyncSlot

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from interface.uart import UART
from UI_crest_debugger import Ui_MainWindow
from page.full_test.full_test import full_test
from common.convert import Data_convertor as cov
from common.UI_object import Right_click_menu_generator, TextBrowser_msg_handler, Timer_generator
# from log.logger import loggers
import logging
logger = logging.getLogger('bluetooth')
logger.setLevel(0)

#sub-module

COM_PORT = 'COM5'
BAUD_RATES = 115200

cov = cov()
dongle = UART(COM_PORT, BAUD_RATES)
# dongle.start()
# dongle.open(COM_PORT, BAUD_RATES)
# dongle.close()
worker = GenericWorker()
do_in_thread = do_in_thread(worker)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        Eng_mode = 0
        hr_monitor_use = 0
        ble_command_use = 0
        cr1_ble_use = 0
        factory_test_func_use = 1
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.dongles_in_port = []
        self.port = COM_PORT
        self.baud_rates = BAUD_RATES
        # self.logger = loggers()
        # self.logger.msg.connect(self.set_UI)
        from page.factory_test.function import factory_test_func
        self.full_test = factory_test_func()
        # self.full_test = full_test()
        self.full_test_Layout.addWidget(self.full_test)
        self.guiwindowtitle = r'EOPI debugger V01.00.00'
        # self.guiwindowtitle = r'FW_Loader_V01.17'

        if Eng_mode:
            # self.tabWidget.addTab(self.logger, 'logger')
            pass
            if hr_monitor_use:
                from page.hr_monitor.hr_monitor import hr_monitor
                self.hr_monitor = hr_monitor()
                self.tabWidget.addTab(self.hr_monitor, 'hr_monitor')

            if ble_command_use:
                from ble_command.ble_command import ble_command
                self.ble_command = ble_command()
                self.tabWidget.addTab(self.ble_command, 'ble_command')

            if cr1_ble_use:
                from page.cr1_ble.command import cr1_ble_command
                self.cr1_ble_command = cr1_ble_command()
                self.tabWidget.addTab(self.cr1_ble_command, 'cr1_ble_command')

            if factory_test_func_use:
                from page.factory_test.function import factory_test_func
                self.factory_test = factory_test_func()
                self.tabWidget.addTab(self.factory_test, 'factory_test_function')

            # self.ble = Bluetooth_LE()
            # self.ble.start()
            # print('run')
            # self.ble.send([0x01])
            # self.ble.send([0x23])
            # self.ble.send([0x23])
            # self.ble.send([0x23])
            # self.ble.send([0x23])
            # self.ble.send([0x23])


        self.tabWidget.setCurrentIndex(0)
        self.setWindowTitle(self.guiwindowtitle)
        self.setWindowIcon(QIcon('cl_icon.ico'))
        if __name__ == '__main__':
            worker.UI.connect(self.set_UI)
        
        ################################################

        #################  module_param ################

        ################################################
        
        # self.tabWidget.tabBarClicked.connect(self.press_up)

        # self.uart_connect_pushButton.clicked.connect(self.trigger_uart)
        # ###############   I2C    ####################
        # I2C_thread.connect_status.connect(self.display_connect_status)
        # I2C_thread.UI.connect(self.set_UI)
        # I2C_thread.module_state.connect(self.set_module_state_label)
        # # self.change_password()
        # I2C_thread.error_log.connect(self.logger.display_msg)
        # self.dongle_id_comboBox.currentIndexChanged.connect(self.set_current_dongle)


        # ###############   dongle    ####################
        # self.timer = {
        #     'Period_check': {'timer': QTimer(), 'interval': 100, 'functions': [self.period_check] },
        # }
        # Timer_generator(self, self.timer)
        # self.timer['Period_check']['timer'].start()

        # self.right_click_menu = {
        #     'port_lineEdit': {
        #         'Reset': {'function': self.reset_module, 'args':{}},
        #         # 'Force_LPMode': {'function': self.force_LPMode, 'args':{}},
        #         # 'Cancel_force_LPMode': {'function': self.cancel_force_LPMode, 'args':{}},
        #         # 'ignore_LP_Pin': {'function': self.ignore_LP_Pin, 'args':{}},
        #         # 'Cancel_ignore_LP_Pin': {'function': self.cancel_ignore_LP_Pin, 'args':{}},
        #         # 'Squelch': {'function': self.squelch, 'args':{}},
        #         # 'Cancel_squelch': {'function': self.cancel_squelch, 'args':{}},
        #     },
        # }
        # Right_click_menu_generator(self, self.right_click_menu)
        


    # @do_in_thread
    # def reset_module(self):
    #     pass

    def trigger_uart(self):
        # if self.uart_connect_pushButton.isChecked():
        #     try:
        #         self.open_uart(self.port, self.baud_rates)
        #     except:
        #         ans = QMessageBox.critical(self,'UART connect fail','Check UART connection and Com port setting')
        # else:
        #     self.close_uart()
        pass

    def period_check(self):
        # self.check_dongle_open()
        pass

    def check_dongle_open(self):
        # if dongle.is_open():
        #     self.uart_connect_pushButton.setChecked(True)
        #     self.uart_connect_pushButton.setText('Connected')
        # else:
        #     self.uart_connect_pushButton.setChecked(False)
        #     self.uart_connect_pushButton.setText('Connect')
        pass

    def open_uart(self, port:str, baud_rate:int):
        # dongle.open(port, baud_rate)
        # self.uart_connect_pushButton.setChecked(True)
        # self.uart_connect_pushButton.setText('Connected')
        pass

    def close_uart(self):
        # dongle.close()
        # self.uart_connect_pushButton.setChecked(False)
        # self.uart_connect_pushButton.setText('Connect')
        pass

    def display_SN(self, datas):
        pass
            
    def display_connect_status(self, status):
        pass

    def set_UI(self, function):
        logger.debug(function)
        function()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
