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

uuid_app_rx = '05DC1984-3B9D-4585-A83B-45C4D3EB0001'
uuid_app_tx = '05DC1984-3B9D-4585-A83B-45C4D3EB0002'

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
        self.bt_device_list = {}

        self.scan_rssi_filter = -50

        # self.cmd_read_tide_pushButton.clicked.connect(self.foo_read_tide_info)
        # self.cmd_write_tide_pushButton.clicked.connect(self.foo_send_tide_info)
        self.connect_pushButton.clicked.connect(self.connect_ble_device)
        self.disconnect_pushButton.clicked.connect(self.disconnect_ble_device)
        self.show_characteristic_pushButton.clicked.connect(self.read_test)
        self.scan_device_pushButton.clicked.connect(self.scan_device)
        self.ble_address_lineEdit.setInputMask('HH:HH:HH:HH:HH:HH')


        if __name__ == '__main__':
            worker.UI.connect(self.set_UI)

    @do_in_thread
    def connect_ble_device(self):
        # try:
        if 1:
            if self.ble.client == None:
                self.ble.select_interface(1)
            self.ble.add_subscribe(uuid_app_rx, True)
            self.ble.add_subscribe(uuid_app_tx, True)
            self.ble.connect(address4)
            # self.handle = self.ble.get_handle()
            self.ble.enable_all_notify()
        # except:
        #     pass

    @do_in_thread
    def disconnect_ble_device(self):
        self.ble.disconnect()

    @do_in_thread
    def scan_device(self):
        worker.UI.emit(lambda: self.display_textBrowser.append(f'RSSI filter = {self.scan_rssi_filter}'))
        self.bt_device_list = {}
        if self.ble.client == None:
            self.ble.select_interface(1)
        # self.ble.write('E0262760-08C2-11E1-9073-0E8AC72E2A23', [0x00])
        self.ble.scan(timeout=5, scan_cb=self.store_scan_data)
        self.display_scan_data()

    @do_in_thread
    def read_test(self):
        a = self.ble.read(uuid_app_rx, [0xa0, 0x00, 0x00, 0x00, 0xff], 1)
        print(a)

    def display_scan_data(self):
        for addr, datas in self.bt_device_list.items():
            device_name = datas['device_name']
            rssi = datas['rssi']
            worker.UI.emit(lambda addr=addr, device_name=device_name, rssi=rssi: self.display_textBrowser.append(f'Address: {addr}, Name: {device_name}, RSSI: {rssi}'))
            # datas = packet_data.get('connectable_advertisement_packet')
            datas = datas['packet_data']
            if datas != None:
                for key2, value2 in datas.items():
                    worker.UI.emit(lambda key2=key2: self.display_textBrowser.append(f'   {key2}'))
                    for key3, value3 in value2.items():
                        worker.UI.emit(lambda key3=key3, value3=value3: self.display_textBrowser.append(f'       {key3}: {value3}'))
            worker.UI.emit(lambda: self.display_textBrowser.append(f'\n'))

    def store_scan_data(self, msg, a, b):
        for key, value in msg.items():
            device_name = value.name
            address = value.address
            rssi = value.rssi
            packet_data = value.packet_data
            if rssi > self.scan_rssi_filter:
                if address not in self.bt_device_list.keys():
                    print(address, self.bt_device_list.keys())
                    self.bt_device_list[address] = {
                        'device_name': device_name,
                        'rssi': rssi,
                        'packet_data': packet_data
                        }
                else:
                    self.bt_device_list[address]['device_name'] = device_name if device_name != ' ' else self.bt_device_list[address]['device_name']

    def add_checksum(self, list):
        pass

            # if address not in self.bt_device_list.keys() and rssi > self.scan_rssi_filter:
            #     print(f'Device Name: {value.name}, Address: {value.address}, RSSI: {value.rssi}, packet: {value.packet_data}')
            #     self.bt_device_list[address] = {
            #         'device_name': device_name,
            #         'rssi': rssi,
            #         'packet_data': packet_data
            #     }
            #     # print(device_name)
            #     worker.UI.emit(lambda: self.display_textBrowser.append(f'Address: {address}, Name: {device_name}, RSSI: {rssi}'))
            #     # datas = packet_data.get('connectable_advertisement_packet')
            #     datas = packet_data
            #     if datas != None:
            #         for key2, value2 in datas.items():
            #             worker.UI.emit(lambda: self.display_textBrowser.append(f'   {key2}'))
            #             for key3, value3 in value2.items():
            #                 worker.UI.emit(lambda: self.display_textBrowser.append(f'       {key3}: {value3}'))
            #     worker.UI.emit(lambda: self.display_textBrowser.append(f'\n'))
            
            # self.display_textBrowser.append('\n')



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

