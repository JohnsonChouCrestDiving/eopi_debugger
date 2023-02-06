#standard library
import sys
import os
import time
import base64
import copy
from collections import namedtuple
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from interface.uart import UART
from common.convert import Data_convertor as cov
from common.UI_object import Right_click_menu_generator, TextBrowser_msg_handler
from common.config import Config_creator
# from log.logger import loggers

#sub-module
if __name__ == '__main__':
    from UI_hr_monitor import Ui_hr_monitor
else:
    from .UI_hr_monitor import Ui_hr_monitor
    
COM_PORT = 'COM7'
BAUD_RATES = 115200

cov = cov()
dongle = UART(COM_PORT, BAUD_RATES)
worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class hr_monitor(QWidget, Ui_hr_monitor):
    
    def __init__(self):
        super(hr_monitor, self).__init__()
        self.setupUi(self)
        self.dongle = dongle

        self.config = Config_creator('hr_monitor')
        self.config_path = self.config.get_path()
        worker.hrMonitor.connect(self.display_uart)

        self.go_to_hr_chart_pushButton.clicked.connect(self.go_to_hr_chart)
        self.go_to_GPS_search_pushButton.clicked.connect(self.go_to_GPS_search)
        self.go_to_GPS_locked_pushButton.clicked.connect(self.go_to_GPS_locked)
        self.go_to_test_mode_pushButton.clicked.connect(self.go_to_test_mode)
        self.SKIP_GPS_pushButton.clicked.connect(self.skip_GPS)
        self.go_to_test_profile_1_pushButton.clicked.connect(self.go_to_test_profile_1)
        self.go_to_test_profile_2_pushButton.clicked.connect(self.go_to_test_profile_2)
        self.go_to_test_profile_3_pushButton.clicked.connect(self.go_to_test_profile_3)
        self.go_to_test_profile_4_pushButton.clicked.connect(self.go_to_test_profile_4)
        self.go_to_test_PAE_pushButton.clicked.connect(self.go_to_test_PAE)
        self.go_to_hr_watch_pushButton.clicked.connect(self.go_to_hr_watch)
        self.go_to_quiet_hr_pushButton.clicked.connect(self.go_to_quiet_hr)
        self.go_to_max_hr_pushButton.clicked.connect(self.go_to_max_hr)
        # self.go_to_test_mode_pushButton.clicked.connect(self.go_to_test_mode)
        # self.logger = loggers()
        # self.logger.msg.connect(self.set_UI)
    def display_uart(self, datas):
        text = ''
        text+= '{:<20} - '.format(datas['file'])
        text+= '{:<5} - '.format(datas['line'])
        text+= '{:<8} - '.format(datas['type'])
        text+= '{:<100}'.format(datas['data'])
        self.uart_display_textBrowser.append(text)
        self.clear_uart_display_pushButton.clicked.connect(self.clear_uart_display_textBrowser)

    @do_in_thread
    def skip_GPS(self):
        self.dongle.sendlines(['SKIP_GPS'])

    @do_in_thread
    def go_to_hr_chart(self):
        self.dongle.sendlines(['BACK_TO_WATCHFACE', 'UP', 'UP'])

    @do_in_thread
    def go_to_GPS_search(self):
        self.dongle.sendlines(['BACK_TO_WATCHFACE', 'OK', 'DOWN', 'OK', 'OK', 'OK'])
    
    
    @do_in_thread
    def go_to_GPS_locked(self):
        self.dongle.sendlines(['BACK_TO_WATCHFACE', 'OK', 'DOWN', 'OK', 'OK', 'OK'])

    @do_in_thread
    def go_to_test_mode(self):
        self.dongle.sendlines(['GO_TO_ENGINEER_MODE', 'OK'])
    
    @do_in_thread
    def go_to_test_profile_1(self):
        self.dongle.sendlines(['GO_TO_ENGINEER_MODE']+['DOWN' for i in range(16)]+['OK'])

    @do_in_thread
    def go_to_test_profile_2(self):
        self.dongle.sendlines(['GO_TO_ENGINEER_MODE']+['DOWN' for i in range(17)]+['OK'])

    @do_in_thread
    def go_to_test_profile_3(self):
        self.dongle.sendlines(['GO_TO_ENGINEER_MODE']+['DOWN' for i in range(18)]+['OK'])

    @do_in_thread
    def go_to_test_profile_4(self):
        self.dongle.sendlines(['GO_TO_ENGINEER_MODE']+['DOWN' for i in range(19)]+['OK'])

    @do_in_thread
    def go_to_test_PAE(self):
        self.dongle.sendlines(['GO_TO_ENGINEER_MODE']+['DOWN' for i in range(21)]+['OK'])\
    @do_in_thread
    def go_to_hr_watch(self):
        self.dongle.sendlines(['BACK_TO_WATCHFACE']+['OK']+['DOWN' for i in range(5)]+['OK'])
    @do_in_thread
    def go_to_quiet_hr(self):
        self.dongle.sendlines(['EVENT_GO_TO_QUIET_HEARTRATE', 'OK'])
        
    @do_in_thread
    def go_to_max_hr(self):
        self.dongle.sendlines(['BACK_TO_WATCHFACE', 'OK', 'DOWN', 'DOWN', 'OK', 'DOWN', 'DOWN', 'OK']
                                +['DOWN' for i in range(8)]+['OK', 'DOWN', 'OK'])
        
    def set_UI(self, function):
        function()
        self.logger.debug(function)

    def clear_uart_display_textBrowser(self):
        self.uart_display_textBrowser.setText('')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = hr_monitor()
    win.show()
    sys.exit(app.exec_())

