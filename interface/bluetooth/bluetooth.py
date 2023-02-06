import sys, os
import threading
import pygatt
import functools

from PyQt5.QtCore import *
from collections import deque
import logging
import time
if __name__ == '__main__':
    from ble_bleak import ble_bleak
    from ble_bluegiga_dongle import ble_bluegiga_dongle
else:
    from .ble_bleak import ble_bleak
    from .ble_bluegiga_dongle import ble_bluegiga_dongle
    
logging.getLogger().setLevel(0)
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

target_name = 'CREST-CR5'
address = 'C2:5E:51:CF:C5:2E'
uuid_i = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
uuid_n = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
uuid_n2 = '6e400004-b5a3-f393-e0a9-e50e24dcca9e'

address4 = 'E8:E9:2E:EC:9E:8A'


class Bluetooth_LE(QThread):
    rx_data = pyqtSignal(dict)

    _instance = None
    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super(Bluetooth_LE, self).__init__()
        self.timeout = 20
        self.commands = deque([])
        self.connect_mark_time = 0
        self.received = deque([])

        # self.subscribe_list = [
        #                             {'uuid': '6e400002-b5a3-f393-e0a9-e50e24dcca9e', 'indication': True},
        #                             {'uuid': '6e400003-b5a3-f393-e0a9-e50e24dcca9e', 'indication': False},
        #                             {'uuid': '6e400004-b5a3-f393-e0a9-e50e24dcca9e', 'indication': False}
        #                             ]
        self.client = None
        self.subscribe_list = []
    
    def add_subscribe(self, uuid:str, indication:bool):
        """_summary_

        Args:
            uuid (str): '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
            indication (bool): True
        """           
        self.subscribe_list.append({'uuid': uuid, 'indication': indication})

    def device_is_connect(func):
        @functools.wraps(func)
        def func_work(self):
            if self.client != None:
                if self.client.is_connect():
                    self.commands.append(functools.partial(func, self))
                    self.start()

        @functools.wraps(func)
        def args_func_work(self, *args, **kwargs):
            if self.client != None:
                if self.client.is_connect():
                    self.commands.append(functools.partial(func, self, *args, **kwargs))
                    self.start()
        
        if func.__code__.co_argcount == 1:
            return func_work
        else:
            return args_func_work

    def select_interface(self, module):
        use_bleak = 0
        use_bluegiga_dongle = 1
        if module == use_bleak:
            self.client = ble_bleak()
        elif module == use_bluegiga_dongle:
            self.client = ble_bluegiga_dongle()
        else:
            pass
    
    def run(self):
        while 1:
            if self.commands:
                cmd = self.commands.popleft()
                cmd()
                self.connect_mark_time = time.time()
            
            if self.check_timeout():
                self.disconnect()
                break
            else:
                time.sleep(0.1)

    def check_timeout(self):
        return time.time() - self.connect_mark_time > self.timeout

    def connect(self, addr):
        if self.client != None and not self.is_connect():
            self.client.connect(addr)
            self.connect_mark_time = time.time()
            
    def is_connect(self):
        return self.client.is_connect()    
    
    # # @device_is_connect    need return
    # def get_handle(self, uuid='6e400002-b5a3-f393-e0a9-e50e24dcca9e'):
    #     handle = self.device.get_handle(uuid)
    #     logger.debug('get_handle: {:02X}'.format(handle))
    #     return handle

    @device_is_connect
    def enable_all_notify(self):
        for info in self.subscribe_list:
            self.subscribe(info['uuid'], info['indication'])

    @device_is_connect
    def subscribe(self, uuid, indication=True):
        self.client.subscribe(uuid, callback=self.handle_received_data, indication=indication)
    
    @device_is_connect
    def send_command(self, uuid, command:list):
        self.client.send_command(uuid, command)
    
    @device_is_connect
    def handle_received_data(self, handle, value):
        logger.debug('receive_data - handle: 0x{:02X}, command: {}'.format(handle, ['{:02X}'.format(i) for i in value]))
        
        self.received.append({'source': 'BLE', 'data': {'handle': handle, 'value': list(value)}})
        self.rx_data.emit({'source': 'BLE', 'data': {'handle': handle, 'value': list(value)}})

    def write(self, uuid, command):
        self.send_command(uuid, command)
        self.get_data(1)        #clear buffer

    def read(self, uuid, command, num)->list:
        self.send_command(uuid, command)
        return self.get_data(num)      

    def get_data(self, num, timeout=5):
        datas = []
        time_mark = time.time()
        count = 0
        while count != num:
            if self.received:
                datas.append(self.received.popleft())
                count+=1
                time_mark = time.time()
            else:
                time.sleep(0.005)
                if time.time() - time_mark > timeout:
                    break
        return datas
    
    def get_single_data(self, timeout=5):
        return self.get_data(1, timeout=timeout)[0]['data']['value'][4:-1]

    @device_is_connect
    def disconnect(self):
        self.client.disconnect()

if __name__ == '__main__':
    a = Bluetooth_LE()
    a.select_interface(0)
    a.connect(address4)
    # a.add_subscribe()
    a.commands.append(lambda: a.send_command('0000180a-0000-1000-8000-00805f9b34fb', [0x2A, 0x23]))
    a.run()
