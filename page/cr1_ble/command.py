#standard library
import sys
import os
import time
import random
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from interface.bluetooth.bluetooth import Bluetooth_LE
from common.convert import Data_convertor as cov
from common.UI_object import Right_click_menu_generator, TextBrowser_msg_handler
from common.config import Config_creator
# from log.logger import loggers
import logging
logger = logging.getLogger('bluetooth')

#sub-module
if __name__ == '__main__':
    from UI_ble_command import Ui_CR1_ble_command
else:
    from .UI_ble_command import Ui_CR1_ble_command
    
address = 'C2:5E:51:CF:C5:2E'
address2 = 'C9:AE:EB:DC:4D:FB'
address3 = 'C3:B4:89:3C:FA:14'
address4 = 'E8:E9:2E:EC:9E:8A'      # apollo3p

cov = cov()
worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class cr1_ble_command(QWidget, Ui_CR1_ble_command):
    
    def __init__(self):
        super(cr1_ble_command, self).__init__()
        self.setupUi(self)

        self.config = Config_creator('cr1_ble_command')
        self.config_path = self.config.get_path()
        self.ble = worker.ble
        self.handle = None
        self.ble.rx_data.connect(self.show_reply)

        # self.cmd_read_tide_pushButton.clicked.connect(self.foo_read_tide_info)
        # self.cmd_write_tide_pushButton.clicked.connect(self.foo_send_tide_info)
        self.connect_pushButton.clicked.connect(self.connect_ble_device)
        self.disconnect_pushButton.clicked.connect(self.disconnect_ble_device)
        self.show_characteristic_pushButton.clicked.connect(self.test)
        self.ble_address_lineEdit.setInputMask('HH:HH:HH:HH:HH:HH')

    @do_in_thread
    def connect_ble_device(self):
        # try:
        if 1:
            self.ble.select_interface(1)
            self.ble.connect(address4)
            # self.handle = self.ble.get_handle()
            self.ble.enable_all_notify()
        # except:
        #     pass

    @do_in_thread
    def disconnect_ble_device(self):
        self.ble.disconnect()

    @do_in_thread
    def test(self):
        self.ble.write('E0262760-08C2-11E1-9073-0E8AC72E2A23', [0x00])



    def show_reply(self, data):
        print(__name__, data)
        self.display_textBrowser.append('handle: 0x{:2X}, value: {}'.format(data['data']['handle'], ['{:02X}'.format(i) for i in data['data']['value']]))
        
        
    def set_UI(self, function):
        function()
        self.logger.debug(function)

    def clear_textBrowser(self):
        self.display_textBrowser.setText('')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = cr1_ble_command()
    win.show()
    sys.exit(app.exec_())

