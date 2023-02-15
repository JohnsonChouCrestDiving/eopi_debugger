import time
from collections import namedtuple, deque
from PyQt5.QtCore import *
import threading
import functools
from .uart import UART
from .bluetooth.bluetooth import Bluetooth_LE
from datetime import datetime
from common.UI_object import Right_click_menu_generator, TextBrowser_msg_handler, Timer_generator
from copy import deepcopy
import re
import logging
logger = logging.getLogger()
# logger.setLevel(0)

def do_in_thread(worker):
    def decorator(func):
        @functools.wraps(func)
        def args_func_work(self, *args, **kwargs):
            if threading.current_thread().name == 'MainThread':
                if worker.func_pool:
                    if worker.func_pool[-1].func.__name__ != func.__name__:
                        worker.func_pool.append(
                            functools.partial(func, self, *args, **kwargs))
                    worker.start()
                else:
                    worker.func_pool.append(
                        functools.partial(func, self, *args, **kwargs))
                    worker.start()
            else:
                return func(self, *args, **kwargs)

        @functools.wraps(func)
        def func_work(self):
            if threading.current_thread().name == 'MainThread':
                if worker.func_pool:
                    if worker.func_pool[-1].func.__name__ != func.__name__:
                        worker.func_pool.append(
                            functools.partial(func, self))
                    
                    worker.start()
                else:
                    worker.func_pool.append(functools.partial(func, self))
                    worker.start()
            else:
                return func(self)
        
        if func.__code__.co_argcount == 1:
            return func_work
        else:
            return args_func_work

    return decorator

class InterfaceWorker(QThread):
    def __init__(self, interface) -> None:
        pass

    def select_interface(self, interface):
        # if interface == 'UART':
        #     self.interface = UART()
        pass


class GenericWorker(QThread):
    hrMonitor           = pyqtSignal(dict)
    UI                  = pyqtSignal(object)

    __instance = None
    def __new__(cls):
        if cls.__instance == None:
            cls.__instance= super().__new__(cls)
        return cls.__instance

    def __init__(self):
        super(GenericWorker, self).__init__()
        self.func_pool = deque([])

        self.data_warehouse = {
            'all': deque([]),
        }
        self.base_type = {
            'file': '',
            'line': 0,
            'type': '',
            'data': '',
        }
        self.data_warehouse_maximum_storage = 10000
        self.data_warehouse_normal_storage = 10000

        self.uart = UART('', 0)
        self.uart.rx_data.connect(self.deal_with_data)

        self.ble = Bluetooth_LE()
        self.ble.rx_data.connect(self.deal_with_data)




    def run(self):
        while self.func_pool:
            # try:
            if 1:
                self.func_pool[0]()
                print(self.func_pool[0])
            # except:
            #     pass
            if self.func_pool:
                self.func_pool.popleft()

    @pyqtSlot(dict)
    def deal_with_data(self, rx_data):
        logger.debug(rx_data)
        source = rx_data['source']
        data = rx_data['data']

        if source == 'UART':
            data_packed = deepcopy(self.base_type)
            try:
                format_data = data.split(' - ')
                if len(format_data)>3:
                    zone = format_data[0].strip().strip(b'\x00'.decode())
                    data_packed['file'] = format_data[1].split('\\')[-1]
                    data_packed['line'] = format_data[2]
                    data_packed['type'] = format_data[3]
                    data_packed['data'] = format_data[4][:-1]       #ignore \n
                    self.data_warehouse['all'].append(data_packed)
                    if(len(self.data_warehouse['all'])>self.data_warehouse_maximum_storage):
                        self.data_warehouse['all'].popleft()

                    if zone not in self.data_warehouse:
                        self.data_warehouse[zone] = deque([])
                    self.data_warehouse[zone].append(data_packed)
                    exec(f"cls.{zone}.emit({data_packed})", {'cls':self})
            except:
                #can't decode
                pass

        elif source == 'BLE':
            # print(data)
            # self.ble_command_data.emit(data)
            # print(data)
            pass

    def format_log_msg(self, level, msg):
        now = datetime.now()
        t = now.strftime("%Y-%m-%d %H:%M:%S")
        thread_name = threading.current_thread().name
        # thread_id = threading.current_thread().ident
        return f'{t:<17} - {level:<8} - {thread_name:<10} - {msg}'

if __name__ =='__main__':
    pass
