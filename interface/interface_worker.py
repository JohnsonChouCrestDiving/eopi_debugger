import time
from collections import namedtuple, deque
from PyQt5.QtCore import QThread, pyqtSignal
import threading
import functools
from .bluetooth.bluetooth import Bluetooth_LE
import logging
logger = logging.getLogger()

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

class GenericWorker(QThread):
    hrMonitor           = pyqtSignal(dict)
    UI                  = pyqtSignal(object)
    message             = pyqtSignal(str)

    __instance = None
    def __new__(cls):
        if cls.__instance == None:
            cls.__instance= super().__new__(cls)
        return cls.__instance

    def __init__(self):
        super(GenericWorker, self).__init__()
        self.func_pool = deque([])
        self.ble = Bluetooth_LE()

    def run(self):
        while 1:
            if self.func_pool:
                self.func_pool[0]()
                logger.debug(f'func_pool: {self.func_pool}')
                if self.func_pool:
                    self.func_pool.popleft()
            else:
                time.sleep(0.1)

if __name__ =='__main__':
    pass
