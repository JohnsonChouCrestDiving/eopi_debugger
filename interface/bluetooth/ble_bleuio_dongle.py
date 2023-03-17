import sys, os
import threading
import functools

from bleuio_lib.bleuio_funcs import BleuIO
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

class ble_bleuio_dongle():
    _instance = None
    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super(ble_bleuio_dongle, self).__init__()
        self.adapter = BleuIO()
        evt_res = self.adapter.at()
        print('ble-bleuio init ', evt_res.Ack['errMsg'])

    def scan(self, timeout=10):
        print(f'ble-bleuio scan ...')
        self.adapter.at_gapscan(timeout=timeout)
        time.sleep(3)
        print("stop scan")
        self.adapter.stop_scan()
    
    def connect(self, addr):
        print(f'ble-bleuio connect {addr}...')
        self.adapter.at_central()
        print(f'ble-bleuio role status: '+ self.adapter.status.role)
        # if CR5, address_type = pygatt.BLEAddressType.random( [1] )
        self.adapter.at_gapconnect(addr, 
                                   intv_min="8", intv_max="8", 
                                   slave_latency="0", sup_timeout="100")
        
        print(f'ble-bleuio connect status: '+ str(self.adapter.status.isConnected))
        if self.adapter.status.isConnected:
            print('connect device info: ', self.adapter.at_get_conn().Rsp)

    def disconnect(self):
        print(f'ble-bleuio disconnect...')
        self.adapter.at_gapdisconnect()
        print(f'ble-bleuio disconnect status: '+ str(self.adapter.status.isConnected))

    def is_connect(self):
        return self.adapter.status.isConnected
    
    def send_command(self, uuid, cmd:list):
        self.adapter.at_central()
        print(f'set ble-bleuio role status: '+ self.adapter.status.role)
        datas_str = self.u8list_to_hexstr(cmd)
        print(f'ble-bleuio send command: uuid: {uuid}, command:{datas_str}')
        # handle = self.get_handel(uuid)
        evt_res = self.adapter.at_gattcwriteb("0905", datas_str)
        print(f'ble-bleuio {uuid} send command status: ',evt_res.Ack['errMsg'])

    def subscribe(self, uuid, evt_callback, scn_callback, indication=True):
        print(f'ble-bleuio enable notify: {uuid}, indication:{indication}')
        try:
            # self.adapter.at_set_indi("""get_handle()""") if indication else self.adapter.at_set_noti("""get_handle()""")
            self.adapter.register_evt_cb(callback=evt_callback)
            self.adapter.register_scan_cb(callback=scn_callback)
            print(f'ble-bleuio enable notify {uuid} status: success')
        except:
            print(f'ble-bleuio enable notify {uuid} status: ERROR !!!!!')

    # def get_handel(self, uuid) -> str:       #TODO
    #     print(f'ble-bleuio get services')
    #     evt_res = self.adapter.at_get_services(uuid)

    def u8list_to_hexstr(self, u8list):
        return ''.join(['{:02X}'.format(x) for x in u8list])