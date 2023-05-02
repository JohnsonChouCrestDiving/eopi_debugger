import sys, os
import threading
import pygatt
import functools

from PyQt5.QtCore import *
import logging
import time
from logging.config import fileConfig

def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS",
            os.path.abspath(".")
        ),
        relative
    )
    
if getattr(sys, 'frozen', None):
    log_file_path = resource_path('logging.conf')
else:
    log_file_path = os.path.join(os.getcwd(), 'log', 'logging.conf')
fileConfig(log_file_path)
logger = logging.getLogger()
logger.setLevel(0)

class ble_bluegiga_dongle():
    _instance = None
    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super(ble_bluegiga_dongle, self).__init__()
        self.adapter = pygatt.BGAPIBackend()
        self.device = None
        self.adapter.start()

    def scan(self, timeout=10, scan_cb=None):
        logger.debug(f'ble-bluegiga scan ...')
        self.adapter.scan(timeout=timeout, scan_cb=scan_cb)
    
    def connect(self, addr):
        logger.debug(f'ble-bluegiga connect {addr}...')
        try:
            # self.adapter.start()
            # if CR5 address_type = pygatt.BLEAddressType.random
            self.device = self.adapter.connect(addr, address_type=pygatt.BLEAddressType.public)
            logger.debug(f'ble-bluegiga connect status: {self.device != None}')
        except:
            logger.debug(f'ble-bluegiga connect ERROR !!!!!')

    def disconnect(self):
        logger.debug(f'ble-bluegiga disconnect...')
        try:
            self.device.disconnect()
            # self.adapter.stop()
            self.device = None
            logger.debug(f'ble-bluegiga disconnect status: {self.device == None}')
        except:
            logger.debug(f'ble-bluegiga disconnect ERROR !!!!!')

    def is_connect(self):
        return self.device != None

    def send_command(self, uuid, datas:list, is_read = False):
        logger.debug(f'ble-bluegiga send command: uuid: {uuid}, command:{datas}')
        self.device.char_write(uuid, bytearray(datas))
        logger.debug(f'ble-bluegiga {uuid} send command status: success')
        # try:
        #     handle = self.get_handle(uuid)
        #     self.device.char_write_handle(handle, bytearray(datas))
        #     logger.debug(f'ble-bluegiga {uuid} send command status: success')
        # except:
        #     logger.debug(f'ble-bluegiga {uuid} send command status: ERROR !!!!!')

    def subscribe(self, uuid, callback, indication=True):
        logger.debug(f'ble-bluegiga enable notify: {uuid}, indication:{indication}')
        try:
            self.device.subscribe(uuid, callback=callback, indication=indication)
            logger.debug(f'ble-bluegiga enable notify {uuid} status: success')
        except:
            logger.debug(f'ble-bluegiga enable notify {uuid} status: ERROR !!!!!')

    def dicover_characteristics(self):
        logger.debug(f'ble-bluegiga dicover characteristics ...')
        return self.adapter.discover_characteristics(1)


    def get_handle(self, uuid='6e400002-b5a3-f393-e0a9-e50e24dcca9e'):
        handle = self.device.get_handle(uuid)
        logger.debug('get_handle: {:02X}'.format(handle))
        return handle


if __name__ == '__main__':
    address4 = 'E8:E9:2E:EC:9E:8A'
    a = ble_bluegiga_dongle()
    a.connect(address4)
    print(a.dicover_characteristics())
    print('finish discover')
    a.disconnect()
