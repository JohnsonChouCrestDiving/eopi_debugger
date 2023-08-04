import sys, os
import threading
import pygatt
import functools

from PyQt5.QtCore import *
from collections import deque
from enum import Enum
import logging
import time
import ctypes
if __name__ == '__main__':
    from ble_bleak import ble_bleak
    from ble_bluegiga_dongle import ble_bluegiga_dongle
    from ble_bleuio_dongle import ble_bleuio_dongle
else:
    from .ble_bleak import ble_bleak
    from .ble_bluegiga_dongle import ble_bluegiga_dongle
    from .ble_bleuio_dongle import ble_bleuio_dongle
    
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
logger = logging.getLogger('rotatingFileLogger')
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

    def scan(self, timeout=10, scan_cb=None):
        if self.client != None:
            self.client.scan(timeout=timeout, scan_cb=scan_cb)
            
    
    def add_subscribe(self, uuid:str, indication:bool):
        """_summary_

        Args:
            uuid (str): '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
            indication (bool): True
        """           
        if uuid not in [i['uuid'] for i in self.subscribe_list]:
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
        if module == dongle.bleak.value:
            self.client = ble_bleak()
        elif module == dongle.blueGiga.value:
            self.client = ble_bluegiga_dongle()
        elif module == dongle.bleuio.value:
            self.client = ble_bleuio_dongle()
        else:
            pass
    
    def run(self):
        while 1:
            if self.commands:
                cmd = self.commands.popleft()
                cmd()
                self.connect_mark_time = time.time()
            
            # if self.check_timeout():
            #     self.disconnect()
            #     break
            # else:
                time.sleep(0.1)

    def check_timeout(self):
        return time.time() - self.connect_mark_time > self.timeout

    def connect(self, addr, addr_type=pygatt.BLEAddressType.random):
        if self.client != None and not self.is_connect():
            self.client.connect(addr, addr_type)
            self.connect_mark_time = time.time()
            
    def is_connect(self):
        return self.client.is_connect()    
    
    # # @device_is_connect    need return
    # def get_handle(self, uuid='6e400002-b5a3-f393-e0a9-e50e24dcca9e'):
    #     handle = self.device.get_handle(uuid)
    #     logger.debug('get_handle: {:02X}'.format(handle))
    #     return handle

    # @device_is_connect
    def dicover_characteristics(self):
        pass

    # @device_is_connect
    def enable_all_notify(self):
        for info in self.subscribe_list:
            self.subscribe(info['uuid'], info['indication'])

    # @device_is_connect
    def subscribe(self, uuid, indication=True):
        self.client.subscribe(uuid, callback=self.handle_received_data, indication=indication)
    
    # @device_is_connect
    def send_command(self, uuid, command:list, is_read:bool):
        self.client.send_command(uuid, command, is_read)
    
    # @device_is_connect
    def handle_received_data(self, handle, value):
        logger.debug('receive_data - handle: 0x{:02X}, command: {}'.format(handle, ['{:02X}'.format(i) for i in value]))
        
        self.received.append({'source': 'BLE', 'data': {'handle': handle, 'value': list(value)}})

    def write(self, uuid, command):
        self.send_command(uuid, command, False)
        self.get_data(1, 0)        #clear buffer

    def read(self, uuid, command, num)->list:
        self.send_command(uuid, command, True)
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

    # @device_is_connect
    def disconnect(self):
        self.client.disconnect()

    def right_without_sign(self, num, bit=0) -> int:
            MAX32INT = 4294967295
            # example: 
            # javascript: -1 >>> 1 === python: right_without_sign(-1, 1)
            val = ctypes.c_uint32(num).value >> bit
            return (val + (MAX32INT + 1)) % (2 * (MAX32INT + 1)) - MAX32INT - 1


    def get_checksum_crc32(self, data):
        crc32Table = [
            0, 1996959894, -301047508, -1727442502, 124634137, 1886057615, -379345611, -1637575261, 249268274, 2044508324, -522852066, -1747789432, 162941995, 2125561021, -407360249, -1866523247, 
            498536548, 1789927666, -205950648, -2067906082, 450548861, 1843258603, -187386543, -2083289657, 325883990, 1684777152, -43845254, -1973040660, 335633487, 1661365465, -99664541, -1928851979, 
            997073096, 1281953886, -715111964, -1570279054, 1006888145, 1258607687, -770865667, -1526024853, 901097722, 1119000684, -608450090, -1396901568, 853044451, 1172266101, -589951537, -1412350631, 
            651767980, 1373503546, -925412992, -1076862698, 565507253, 1454621731, -809855591, -1195530993, 671266974, 1594198024, -972236366, -1324619484, 795835527, 1483230225, -1050600021, -1234817731, 
            1994146192, 31158534, -1731059524, -271249366, 1907459465, 112637215, -1614814043, -390540237, 2013776290, 251722036, -1777751922, -519137256, 2137656763, 141376813, -1855689577, -429695999, 
            1802195444, 476864866, -2056965928, -228458418, 1812370925, 453092731, -2113342271, -183516073, 1706088902, 314042704, -1950435094, -54949764, 1658658271, 366619977, -1932296973, -69972891, 
            1303535960, 984961486, -1547960204, -725929758, 1256170817, 1037604311, -1529756563, -740887301, 1131014506, 879679996, -1385723834, -631195440, 1141124467, 855842277, -1442165665, -586318647, 
            1342533948, 654459306, -1106571248, -921952122, 1466479909, 544179635, -1184443383, -832445281, 1591671054, 702138776, -1328506846, -942167884, 1504918807, 783551873, -1212326853, -1061524307, 
            -306674912, -1698712650, 62317068, 1957810842, -355121351, -1647151185, 81470997, 1943803523, -480048366, -1805370492, 225274430, 2053790376, -468791541, -1828061283, 167816743, 2097651377, 
            -267414716, -2029476910, 503444072, 1762050814, -144550051, -2140837941, 426522225, 1852507879, -19653770, -1982649376, 282753626, 1742555852, -105259153, -1900089351, 397917763, 1622183637, 
            -690576408, -1580100738, 953729732, 1340076626, -776247311, -1497606297, 1068828381, 1219638859, -670225446, -1358292148, 906185462, 1090812512, -547295293, -1469587627, 829329135, 1181335161, 
            -882789492, -1134132454, 628085408, 1382605366, -871598187, -1156888829, 570562233, 1426400815, -977650754, -1296233688, 733239954, 1555261956, -1026031705, -1244606671, 752459403, 1541320221, 
            -1687895376, -328994266, 1969922972, 40735498, -1677130071, -351390145, 1913087877, 83908371, -1782625662, -491226604, 2075208622, 213261112, -1831694693, -438977011, 2094854071, 198958881, 
            -2032938284, -237706686, 1759359992, 534414190, -2118248755, -155638181, 1873836001, 414664567, -2012718362, -15766928, 1711684554, 285281116, -1889165569, -127750551, 1634467795, 376229701, 
            -1609899400, -686959890, 1308918612, 956543938, -1486412191, -799009033, 1231636301, 1047427035, -1362007478, -640263460, 1088359270, 936918000, -1447252397, -558129467, 1202900863, 817233897, 
            -1111625188, -893730166, 1404277552, 615818150, -1160759803, -841546093, 1423857449, 601450431, -1285129682, -1000256840, 1567103746, 711928724, -1274298825, -1022587231, 1510334235, 755167117
        ]
        crc = -1
        for i in range(len(data)):
            crc = crc32Table[(crc & 255) ^ (data[i] & 255)] ^ self.right_without_sign(crc, 8)
        return (crc ^ -1) & 0xffffffff

    def get_checksum(self, data):
        crc = 0x00
        for i in range(len(data)):
            crc ^= data[i]
            for j in range(8):
                if (crc & 0x80) != 0:
                    crc = (crc << 1) ^ 0x07
                else:
                    crc <<= 1
        return crc & 0xff

class dongle(Enum):
    bleak       = 0
    blueGiga    = 1
    bleuio      = 2

if __name__ == '__main__':
    a = Bluetooth_LE()
    a.select_interface(0)
    a.connect(address4)
    # a.add_subscribe()
    a.commands.append(lambda: a.send_command('0000180a-0000-1000-8000-00805f9b34fb', [0x2A, 0x23]))
    a.run()
