#standard library
import sys
import os
import time
import base64
import copy
import random
from collections import namedtuple
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
    from UI_ble_command import Ui_ble_command
else:
    from .UI_ble_command import Ui_ble_command
    
address = 'C2:5E:51:CF:C5:2E'
address2 = 'C9:AE:EB:DC:4D:FB'
address3 = 'C3:B4:89:3C:FA:14'
address4 = 'E8:E9:2E:EC:9E:8A'

cov = cov()
worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class ble_command(QWidget, Ui_ble_command):
    
    def __init__(self):
        super(ble_command, self).__init__()
        self.setupUi(self)

        self.config = Config_creator('ble_command')
        self.config_path = self.config.get_path()
        self.ble = Bluetooth_LE(address4)
        self.handle = None
        self.ble.rx_data.connect(self.show_reply)

        self.cmd_read_tide_pushButton.clicked.connect(self.foo_read_tide_info)
        self.cmd_write_tide_pushButton.clicked.connect(self.foo_send_tide_info)
        self.ble_connect_pushButton.clicked.connect(self.connect_ble_device)
        self.ble_address_lineEdit.setInputMask('HH:HH:HH:HH:HH:HH')

    @do_in_thread
    def connect_ble_device(self):
        # try:
        if 1:
            self.ble.connect_device()
            self.handle = self.ble.get_handle()
            self.ble.enable_all_notify()
        # except:
        #     pass

    @do_in_thread
    def foo_read_tide_info(self):
        data = self.ble.read(self.handle, cov.crest_add_cksum([0xB0, 0x03, 0x01, 0x00]), 1)[0]
        location = cov.intList_to_ASCII(data['data']['value'][4:-1])
        print(location)

        for i in range(1, 31):
            self.ble.read(self.handle, cov.crest_add_cksum([0xB0, 0x03, 0x01, i]), 1)

    @do_in_thread
    def foo_send_tide_info(self):
        
        #clear buffer
        self.ble.write(self.handle, cov.crest_add_cksum([0xB0, 0x03, 0x00, 0x1F]))

        #send name
        data_list = [0xB0, 0x03, 0x00, 00]
        data_list.extend((cov.ASCII_to_u8_list('Keelung')))
        data_list = cov.file_u8_list_with(data_list, 0x00, 19)
        self.ble.write(self.handle, cov.crest_add_cksum(data_list))

        #send timezone
        data_list = [0xB0, 0x03, 0x00, 0x21, 0x0E]
        self.ble.write(self.handle, cov.crest_add_cksum(data_list))

        #send daylightsaving
        data_list = [0xB0, 0x03, 0x00, 0x22, 0x00]
        self.ble.write(self.handle, cov.crest_add_cksum(data_list))

        #send data
        utc = int(time.time() - 24*60*60*2)
        for i in range(1, 31):
            utc+=6*60*60
            # i = 1
            # if 1:
            if i%2:
                height = int(random.uniform(0,10.0)*10)
            else:
                height = int(random.uniform(-10.0,0)*10)
            typ = i%2

            data_list = [0xB0, 0x03, 0x00, i]
            data_list.extend(cov.swap_endian(cov.i32_to_u8_list(utc)))
            data_list.extend(cov.swap_endian(cov.i16_to_u8_list(height)))
            data_list.extend([typ])
            self.ble.write(self.handle, cov.crest_add_cksum(data_list))

        #store data
        self.ble.write(self.handle, cov.crest_add_cksum([0xB0, 0x03, 0x00, 0x20]))

        
        #send display hr
        data_list = [0xB0, 0x03, 0x00, 0x23, 24]
        self.ble.write(self.handle, cov.crest_add_cksum(data_list))


    
    @do_in_thread
    def read_fw_version(self):
        self.ble.send_command(self.handle, [0x23])
        version = self.ble.get_data(1)

    def show_reply(self, data):
        print(__name__, data)
        self.display_textBrowser.append('handle: 0x{:2X}, value: {}'.format(data['data']['handle'], ['{:02X}'.format(i) for i in data['data']['value']]))
        
        
    def set_UI(self, function):
        function()
        self.logger.debug(function)

    def clear_uart_display_textBrowser(self):
        self.display_textBrowser.setText('')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = hr_monitor()
    win.show()
    sys.exit(app.exec_())

