import sys,os
import threading
import functools
import re
import time
import logging

from .bleuio.bleuio_lib.bleuio_funcs import BleuIo
from collections import defaultdict
from datetime import datetime
from logging.config import fileConfig
from binascii import unhexlify
from common.convert import Data_convertor as cov
from pygatt.backends import BLEBackend, Characteristic, BLEAddressType
from pygatt.backends.bgapi.bgapi import AdvertisingAndScanInfo


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
logger = logging.getLogger('RotatingFileHandler')
logger.setLevel(0)
cov = cov()


class ble_bleuio_dongle():
    def __init__(self):
        self._adapter = BleuIo(debug=False)
        self._adapter.start_daemon()
        self._peripheral_GATT_table = []
        self._callbacks = defaultdict(set)
    
    def connect(self, mac_address, ble_address_type = BLEAddressType.public, timeout = 0,
                intv_min = '30', intv_max = '30', latency = '0', sup_timeout = '1000'):
    # intv_min:7.5ms~4s, intv_max:7.5ms~4s, slave_latency:0~499, sup_timeout:100ms~32s
    # defult: intv_min=30ms, intv_max=30ms, slave_latency=0, sup_timeout=1000ms
        if self.is_connect():
            logger.info('ble-bleuio disconnected previous connection...')
            self.disconnect()
        
        if self._get_GAP_role() != 'Central role':
            self._set_in_central_role()

        if ble_address_type == BLEAddressType.public:
            ble_addr = "[0]" + mac_address
        elif ble_address_type == BLEAddressType.random:
            ble_addr = "[1]" + mac_address

        self._adapter.atds(False)
        logger.info(f'ble-bleuio connect {ble_addr}...')
        if timeout != 0 or intv_min!='30' or intv_max!='30' or latency!='0' or sup_timeout!='1000':
            rx_res = self._adapter.at_gapconnect(ble_addr, timeout,
                                                 intv_min, intv_max, 
                                                 latency, sup_timeout)
        else:
            rx_res = self._adapter.at_gapconnect(ble_addr)

        self._generate_GATT_table()

        return rx_res

    def _get_GAP_role(self):
        while 1:
            rx_res = self._adapter.at_gapstatus()
            try:
                elements = rx_res[0].split('\r\n')
            except:
                continue
            if elements.__len__() > 1: break

        GAP_role = elements[1] # 取出需要的元素
        logger.debug(f'ble-bleuio GAP role: {GAP_role}')
        return GAP_role
        """
        rx_res example:
        [
            '\r\r\n
            Central role\r\n
            \r\n
            Not Connected\r\n
            \r\n
            Not Advertising\r\n'
        ]
        """
    
    def is_connect(self):
        # rx_response of bleuio dongle return isn't safe, so use GATT table to check connected status
        # return self._peripheral_GATT_table.__len__() > 0
        while 1:
            rx_res = self._adapter.at_gapstatus()
            try:
                elements = rx_res[0].split('\r\n')
            except:
                continue
            if elements.__len__() > 3: break

        connected_status = elements[3] # 取出需要的元素
        if connected_status == 'Connected':
            logger.info('ble-bleuio already connected peripheral')
        else:
            logger.warning('ble-bleuio not connected peripheral')
        return connected_status == 'Connected'
    
    def _is_advertising(self):
        while 1:
            rx_res = self._adapter.at_gapstatus()
            try:
                elements = rx_res[0].split('\r\n')
            except:
                continue
            if elements.__len__() > 5: break

        advertising_status = elements[5] # 取出需要的元素
        logger.debug(f'ble-bleuio is {advertising_status}')
        return advertising_status == 'Advertising'
    
    def _set_in_central_role(self):
        logger.debug(f'ble-bleuio set in central role...')
        rx_res = self._adapter.at_central()
        return rx_res
    
    def _set_handle_in_indication(self, handle:str):
        logger.info(f'ble-bleuio set handle: {handle} indication...')
        rx_res = self._adapter.at_set_indi(handle)
        return rx_res
    
    def _set_handle_in_notification(self, handle:str):
        logger.info(f'ble-bleuio set handle: {handle} notification...')
        rx_res = self._adapter.at_set_noti(handle)
        return rx_res
    
    def send_command(self, uuid:str, cmd_list:list, is_read: bool):
        handle = self._get_handle(uuid)
        cmd = cov.u8_list_to_hexstr(cmd_list)
        logger.info(f'ble-bleuio send command: handle:{handle}, command:{cmd}')

        try:
            if handle is None:
                logger.error(f'ble-bleuio uuid: {uuid} does not exist')
            else:
                if len(cmd) < 1:
                    logger.warning('ble-bleuio command is empty')
                if is_read:
                    rx_res = self._adapter.at_gattcwriteb(handle, cmd)
                    logger.info(f'ble-bleuio {uuid} send command status: success')
                    self._receive_notification(rx_res)
                    return rx_res
                else:
                    rx_res = self._adapter.at_gattcwritewrb(handle, cmd)
                    logger.info(f'ble-bleuio {uuid} send command status: success')
                    return rx_res
        except:
            logger.error(f'ble-bleuio {uuid} send command status: fail')
 
    def disconnect(self):
        logger.info(f'ble-bleuio disconnect...')
        try:
            rx_res = self._adapter.at_gapdisconnectall()
            self._peripheral_GATT_table = []
            logger.info('ble-bleuio disconnect success')
        except:
            logger.error(f'ble-bleuio disconnect fail: {rx_res}')
        # self._adapter.stop_daemon()
        return rx_res
    
    def _get_handle(self, uuid:str) -> str:
        uuid = uuid.lower()
        handle = None
        logger.debug(f'ble-bleuio get {uuid} handle...')

        debug_cnt = 0
        while len(self._peripheral_GATT_table) == 0 and debug_cnt < 3:
            self._generate_GATT_table()
            debug_cnt += 1
        
        for item in self._peripheral_GATT_table:
            if item[2] == uuid:
                handle = item[0]
                break

        if handle is not None:
            logger.debug(f'ble-bleuio get {uuid} handle: {item[0]}')
            return handle
        else:
            logger.warning(f'ble-bleuio No found characteristic matching {uuid}')
            return None
    
    def _generate_GATT_table(self, simulat_dat = None):
        """
        Generate the GATT table of the connected peripheral.
        Example:
            transform the string:
            ['\r\r\nOK\r\n', 
             '\t0011 serv 0x1801\r\n', 
             '\t0012 char 0x1801 prop=32 (-R--NI--)\r\n
             \t0013 ---- 0x2a05\r\n', 
             '\t0020 serv 6e400001-b5a3-f393-e0a9-e50e24dcca9e\r\n', 
             '\t0021 char 6e400001-b5a3-f393-e0a9-e50e24dcca9e prop=2c (--XW-I--)\r\n
             \t0022 ---- 6e400002-b5a3-f393-e0a9-e50e24dcca9e\r\n
             \t0023 desc 0x2902\r\n
             \t0024 char 6e400001-b5a3-f393-e0a9-e50e24dcca9e prop=10 (----N---)\r\n
             \t0025 ---- 6e400003-b5a3-f393-e0a9-e50e24dcca9e\r\n
             \t0026 desc 0x2902\r\n
             \t0027 char 6e400001-b5a3-f393-e0a9-e50e24dcca9e prop=10 (----N---)\r\n
             \t0028 ---- 6e400004-b5a3-f393-e0a9-e50e24dcca9e\r\n
             \t0029 desc 0x2902\r\n
             \r\nhandle_evt_gattc_browse_completed: conn_idx=0000 status=0\r\n
             \r\nhandle_evt_gattc_write_completed: conn_idx=0000 handle=0000 status=0\r\n']
            
            to list:
            [
                ('0011', 'serv', '0x1801'), 
                ('0012', 'char', '0x1801', 'prop=32', '(-R--NI--)'), 
                ('0013', '----', '0x2a05'), 
                ('0020', 'serv', '6e400001-b5a3-f393-e0a9-e50e24dcca9e'), 
                ('0021', 'char', '6e400001-b5a3-f393-e0a9-e50e24dcca9e', 'prop=2c', '(--XW-I--)'), 
                ('0022', '----', '6e400002-b5a3-f393-e0a9-e50e24dcca9e'), 
                ('0023', 'desc', '0x2902'), 
                ('0024', 'char', '6e400001-b5a3-f393-e0a9-e50e24dcca9e', 'prop=10', '(----N---)'), 
                ('0025', '----', '6e400003-b5a3-f393-e0a9-e50e24dcca9e'), 
                ('0026', 'desc', '0x2902'), 
                ('0027', 'char', '6e400001-b5a3-f393-e0a9-e50e24dcca9e', 'prop=10', '(----N---)'), 
                ('0028', '----', '6e400004-b5a3-f393-e0a9-e50e24dcca9e'), 
                ('0029', 'desc', '0x2902')
            ]
        """
        # 原始字符串
        logger.debug(f'ble-bleuio get all services...')
        if len(self._adapter.atds(True)) != 0:
            s = ''.join(self._adapter.at_get_services() if simulat_dat is None else simulat_dat)
            time.sleep(0.1)

        # 使用正則表達式將字符串轉換為list
        lst = re.findall(r'\t(\d+)\s+([\w-]+)\s+(.*?)\s*$', s, re.M)

        # 提取所需的信息
        result = []
        for item in lst:
            num, key, val = item
            if key == '----':
                result.append((num, key, val.strip()))
            else:
                parts = val.split(' ')
                props = parts[1:]
                result.append((num, key, parts[0], *props))

        # 輸出結果
        if len(result) != 0:
            logger.info(f'ble-bleuio peripheral GATT table:{result}')
            self._peripheral_GATT_table = result
        else:
            logger.error("ble-bleuio no found services, check if you are connected.")
    
    def subscribe(self, uuid, callback = None, indication=True):
        logger.debug(f'ble-bleuio enable notify: {uuid}, indication:{indication}')
        handle = self._get_handle(uuid)
        if handle is None:
            logger.warning('ble-bleuio enable notify failed: no such uuid')
            return
        try:
            if indication:
                self._set_handle_in_indication(handle)
            else:
                self._set_handle_in_notification(handle)
            
            if callback is not None:
                self._callbacks[handle].add(callback)
            logger.debug(f'ble-bleuio enable notify {uuid} status: success')
        except:
            logger.error(f'ble-bleuio enable notify {uuid} status: ERROR !!!')

    def scan(self, timeout, scan_cb=None):
        if self._get_GAP_role() != 'Central role':
            self._set_in_central_role()
        logger.info(f'ble-bleuio scan ...')
        self._adapter.at_gapscan(timeout=timeout)
        devices = self._process_scan_response()
        logger.debug("stop scan")
        self._adapter.stop_scan()
        scan_cb(devices, 'ff:ff:ff:ff:ff:ff', 0) # The last two parameters will be put into addr and pecket_type in bluegiga api

    def _process_notification_header(self, data: list):
        header_info = data.split(' ')
        evt_gattc_handle = header_info[0]
        RAW_conn_idx = header_info[1]
        RAW_handle = header_info[2]
        RAW_length = header_info[3]

        if evt_gattc_handle == 'handle_evt_gattc_notification:':
            indi_or_noti_handle = 'notification'
        elif evt_gattc_handle == 'handle_evt_gattc_indication:':
            indi_or_noti_handle = 'indication'
        conn_idx: str = RAW_conn_idx.split('=')[1]
        handle: str = RAW_handle.split('=')[1]
        length: str = RAW_length.split('=')[1]

        return (indi_or_noti_handle, conn_idx, handle, length)

    def _receive_notification(self, cwriteb_rx_res: list):
        """
        把整個list用join()變成同一個字串,再用\r\n分割,然後再去分析
        """
        try:
            if len(cwriteb_rx_res) != 0:
                data_first_process = ''.join(cwriteb_rx_res)
                data_second_process = data_first_process.split('\r\n')
                for i in range (len(data_second_process)):
                    if i < 6 or data_second_process[i] is None:
                        continue
                    elif i % 6 == 0:
                        handle_type, conn_idx_in_bleuio, handle, variable_length = (
                            self._process_notification_header(data_second_process[i])
                        )
                    elif i % 6 == 2:
                        Value_received = data_second_process[i].split(':')[1].strip()
                    elif i % 6 == 3:
                        Hex = data_second_process[i].split(':')[1].strip()
                    elif i % 6 == 4:
                        msg_size = data_second_process[i].split(':')[1].strip()
                        if handle in self._callbacks:
                            for callback in self._callbacks[handle]:
                                callback(int(handle), list(unhexlify(Hex[2:])))
        except:
            logger.error(f'ble-bleuio convert cwriteb() Rx response fail,cwriteb_rx_res: {cwriteb_rx_res}')
        """
            The cwriteb_rx_res data example:
            [
                'AT+GATTCWRITEB=0022 3800444956454C4F47\r\r\n
                DATA WRITTEN: 3800444956454C4F47\r\n
                Size: 9\r\n', 

                '\r\n
                handle_evt_gattc_write_completed: conn_idx=0000 handle=0022 status=0\r\n
                \r\n
                handle_evt_gattc_notification: conn_idx=0000 handle=0025 length=18\r\n
                \r\n
                Value received: \r\n
                Hex: 0x0000354134443635303338030000F0880000\r\n
                Size: 18\r\n
                \r\n
                handle_evt_gattc_notification: conn_idx=0000 handle=0025 length=18\r\n
                \r\n
                Value received: \x01\r\n
                Hex: 0x01003541344436353246B8020000FE470000\r\n
                Size: 18\r\n
                \r\n
                handle_evt_gattc_indication: conn_idx=0000 handle=0022 length=3\r\n
                \r\n
                Value received: 8\x02\r\n
                Hex: 0x380200\r\n
                Size: 3\r\n'
            ]
            """

    def _process_scan_response(self):
        """
        return = {
            (str)address: {name: (str)name, address: (str)address, rssi: (int)rssi, packet_data: None},
            ...
        }
        """
        rtn = {}
        devces = ''.join(self._adapter.rx_scanning_results[1:]).split('\r\n\r\n')
        try:
            for dev_data in devces:
                data_items  = dev_data.split(' ')
                # This information is only fetched if the device has a name.
                # Device name may include spaces.
                name = dev_data.split("(")[1].split(")")[0] if len(data_items) > 6 else 'Unknown'

                if data_items[2] not in rtn.keys():
                    rtn[data_items[2]] = {
                        'name': name, 
                        'address': data_items[2], 
                        'rssi': int(data_items[5]), 
                        'pkt_dat': None
                    }
                else:
                    if rtn[data_items[2]]['name'] != name:
                        rtn[data_items[2]]['name'] = name
                    if rtn[data_items[2]]['rssi'] != int(data_items[5]):
                        rtn[data_items[2]]['rssi'] = int(data_items[5])
                logger.debug(
                    f'Received a scan response from {data_items[2]} with rssi={int(data_items[5])} dBM'
                )
        except:
            logger.error(f'ble-bleuio convert scan response fail, dev_data: {dev_data}')
            
        return rtn
        """
        The rx_scanning_results example:
        [
            '\r\r\nSCANNING...\r\n', 
            '\r\n[01] Device: [1]15:D8:29:9B:89:6F  RSSI: -44\r\n', 
            '\r\n[02] Device: [1]24:C2:BB:B8:21:A0  RSSI: -78\r\n\r\n[03] Device: [1]0F:36:2A:F9:C2:93  RSSI: -71\r\n\r\n[04] Device: [1]0B:AB:39:7B:52:93  RSSI: -81\r\n\r\n[05] Device: [1]21:1C:4C:1C:23:30  RSSI: -61\r\n\r\n[06] Device: [1]2D:D9:D8:5E:63:D1  RSSI: -53\r\n', 
            '\r\n[07] Device: [1]42:D3:6E:74:E8:2E  RSSI: -63\r\n\r\n[08] Device: [1]E8:7A:85:7D:30:83  RSSI: -75\r\n\r\n[08] Device: [1]E8:7A:85:7D:30:83  RSSI: -75 (Buds2 Pro)\r\n\r\n[09] Device: [1]50:BF:BD:1D:9D:BE  RSSI: -75\r\n\r\n[10] Device: [1]79:D9:20:E5:9C:28  RSSI: -68\r\n', 
            '\r\n[11] Device: [1]70:07:AA:23:1E:A9  RSSI: -77\r\n\r\n[12] Device: [1]03:04:9A:36:93:CB  RSSI: -76\r\n\r\n[13] Device: [0]18:EE:69:2B:C4:0C  RSSI: -78\r\n\r\n[14] Device: [1]76:82:88:3B:5F:20  RSSI: -60\r\n\r\n[15] Device: [1]E7:F4:C0:FE:9C:3D  RSSI: -79\r\n\r\n[16] Device: [1]4C:C8:33:58:FC:D9  RSSI: -77\r\n', 
            '\r\n[17] Device: [1]74:7A:14:FD:E6:1B  RSSI: -83\r\n', 
            '\r\n[18] Device: [1]C0:A0:0D:52:07:5B  RSSI: -66 (CREST-CR5\x03)\r\n\r\n[19] Device: [1]13:29:61:D8:EA:48  RSSI: -77\r\n\r\n[20] Device: [1]10:A1:4F:EB:0E:05  RSSI: -66\r\n', 
            '\r\n[21] Device: [0]44:73:D6:50:63:25  RSSI: -86\r\n\r\n[21] Device: [0]44:73:D6:50:63:25  RSSI: -86 (MeetUp Soft Remote)\r\n\r\n[22] Device: [1]C0:07:64:16:74:97  RSSI: -57 (CREST-CR5\x03)\r\n', 
            '\r\n[23] Device: [1]2F:80:CA:D7:42:7B  RSSI: -77\r\n', 
            '\r\n[24] Device: [1]C3:84:6F:29:BE:67  RSSI: -81 (CREST-CR5\x03)\r\n', 
            '\r\n[25] Device: [1]CA:DE:47:DE:62:FC  RSSI: -83 (CREST-CR5\x03)\r\n', 
            '\r\n[26] Device: [1]53:41:13:DD:E6:84  RSSI: -77\r\n', 
            '\r\n[27] Device: [1]D0:4E:F6:74:A6:2A  RSSI: -56\r\n', 
            '\r\n[28] Device: [1]CC:5E:49:15:CF:36  RSSI: -84 (CREST-CR5\x03)\r\n\r\n[29] Device: [1]CE:37:A8:0E:3A:92  RSSI: -91 (CREST-CR5\x03)\r\n', 
            '\r\n[30] Device: [1]70:73:89:5F:8F:95  RSSI: -90\r\n', 
            '\r\n[31] Device: [1]C9:21:EE:87:53:D4  RSSI: -72\r\n', 
            '\r\n[32] Device: [1]C6:3B:D5:50:11:8C  RSSI: -85 (CREST-CR5\x03)\r\n', 
            '\r\n[33] Device: [1]FD:39:95:F3:F8:24  RSSI: -72 (SMI-M1S)\r\n'
        ]
        """

    # def read(self, uuid):
    #     logger.debug(f'ble-bleuio read: {uuid}')
    #     try:
    #         self._adapter.at_gattcread(self._get_handle(uuid))
    #         time.sleep(1)
    #         logger.debug(f'ble-bleuio read {uuid} status: success')
    #     except:
    #         logger.error(f'ble-bleuio read {uuid} status: ERROR !!!')

    def __exit__(self):
        self._adapter.stop_daemon()


if __name__ == '__main__':
    bleuio = ble_bleuio_dongle()

    # # CR1
    # addr = "E8:E9:2E:EC:9E:8A"
    # ble_addr_type = BLEAddressType.public
    # uuid = "05DC1984-3B9D-4585-A83B-45C4D3EB0001"
    # cmd_list = [0xA0, 0x00, 0x00, 0x00, 0xFF]

    # CR5
    addr = "C3:B4:89:3C:FA:14"
    uuid = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
    ble_addr_type = BLEAddressType.random
    # cmd_list = [0xA0, 0x01, 0x01, 0x5D] # get fw verson
    # cmd_list = [0xA0, 0x00, 0x00, 0x5F] # where is my watch
    cmd_list = [0x38, 0x00, 0x44, 0x49, 0x56, 0x45, 0x4c, 0x4f, 0x47] # Directory Browse All File Info


    bleuio.connect(addr, ble_addr_type)

    # bleuio.subscribe(uuid, callback=handle_received_data)
    # bleuio.subscribe(uuid="6e400003-b5a3-f393-e0a9-e50e24dcca9e", callback=handle_received_data, indication=False)
    bleuio.send_command(uuid, cmd_list)

    bleuio.disconnect()


    # r = ['AT+GATTCWRITEB=0022 3800444956454C4F47\r\r\nDATA WRITTEN: 3800444956454C4F47\r\nSize: 9\r\n', 
    #     '\r\nhandle_evt_gattc_write_completed: conn_idx=0000 handle=0022 status=0\r\n\r\nhandle_evt_gattc_notification: conn_idx=0000 handle=0025 length=18\r\n\r\nValue received: \r\nHex: 0x0000354134443635303338030000F0880000\r\nSize: 18\r\n\r\nhandle_evt_gattc_notification: conn_idx=0000 handle=0025 length=18\r\n\r\nValue received: \x01\r\nHex: 0x01003541344436353246B8020000FE470000\r\nSize: 18\r\n\r\nhandle_evt_gattc_indication: conn_idx=0000 handle=0022 length=3\r\n\r\nValue received: 8\x02\r\nHex: 0x380200\r\nSize: 3\r\n'
    # ]
    # bleuio._receive_notification(r)

"""
=========================== GATT table renference: ============================
"""
"""
CR1:
    bleuio._peripheral_GATT_table = [
        ('0010', 'serv', '0x1801'), 
        ('0011', 'char', '0x1801', 'prop=20', '(-----I--)'), 
        ('0012', '----', '0x2a05'), 
        ('0013', 'desc', '0x2902'), 
        ('0014', 'char', '0x1801', 'prop=02', '(-R------)'), 
        ('0015', '----', '0x2b29'), 
        ('0016', 'char', '0x1801', 'prop=02', '(-R------)'), 
        ('0017', '----', '0x2b2a'), 
        ('0030', 'serv', '0x180a'), 
        ('0031', 'char', '0x180a', 'prop=02', '(-R------)'), 
        ('0032', '----', '0x2a29'), 
        ('0033', 'char', '0x180a', 'prop=02', '(-R------)'), 
        ('0034', '----', '0x2a23'), 
        ('0035', 'char', '0x180a', 'prop=02', '(-R------)'), 
        ('0036', '----', '0x2a24'), 
        ('0037', 'char', '0x180a', 'prop=02', '(-R------)'),
        ('0038', '----', '0x2a25'),
        ('0039', 'char', '0x180a', 'prop=02', '(-R------)'), 
        ('0040', '----', '0x2a2a'), 
        ('0800', 'serv', '05dc1984-3b9d-4585-a83b-45c4d3eb1011'), 
        ('0801', 'char', '05dc1984-3b9d-4585-a83b-45c4d3eb1011', 'prop=04', '(--X-----)'), 
        ('0802', '----', '05dc1984-3b9d-4585-a83b-45c4d3eb0011'), 
        ('0803', 'char', '05dc1984-3b9d-4585-a83b-45c4d3eb1011', 'prop=10', '(----N---)'), 
        ('0804', '----', '05dc1984-3b9d-4585-a83b-45c4d3eb0012'), 
        ('0805', 'desc', '0x2902'), 
        ('0806', 'char', '05dc1984-3b9d-4585-a83b-45c4d3eb1011', 'prop=14', '(--X-N---)'), 
        ('0807', '----', '05dc1984-3b9d-4585-a83b-45c4d3eb0013'), 
        ('0808', 'desc', '0x2902'), 
        ('0820', 'serv', '05dc1984-3b9d-4585-a83b-45c4d3eb1001'), 
        ('0821', 'char', '05dc1984-3b9d-4585-a83b-45c4d3eb1001', 'prop=04', '(--X-----)'), 
        ('0822', '----', '05dc1984-3b9d-4585-a83b-45c4d3eb1002'), 
        ('0823', 'char', '05dc1984-3b9d-4585-a83b-45c4d3eb1001', 'prop=10', '(----N---)'), 
        ('0824', '----', '05dc1984-3b9d-4585-a83b-45c4d3eb1003'), 
        ('0825', 'desc', '0x2902'), 
        ('0900', 'serv', '05dc1984-3b9d-4585-a83b-45c4d3eb0000'), 
        ('0901', 'char', '05dc1984-3b9d-4585-a83b-45c4d3eb0000', 'prop=10', '(----N---)'), 
        ('0902', '----', '05dc1984-3b9d-4585-a83b-45c4d3eb0002'), 
        ('0903', 'desc', '0x2902'), 
        ('0904', 'char', '05dc1984-3b9d-4585-a83b-45c4d3eb0000', 'prop=2c', '(--XW-I--)'), 
        ('0905', '----', '05dc1984-3b9d-4585-a83b-45c4d3eb0001'), 
        ('0906', 'desc', '0x2902')
    ]
"""
"""
CR5:
    bleuio._peripheral_GATT_table = [
        ('0011', 'serv', '0x1801'), 
        ('0012', 'char', '0x1801', 'prop=32', '(-R--NI--)'), 
        ('0013', '----', '0x2a05'), 
        ('0020', 'serv', '6e400001-b5a3-f393-e0a9-e50e24dcca9e'), 
        ('0021', 'char', '6e400001-b5a3-f393-e0a9-e50e24dcca9e', 'prop=2c', '(--XW-I--)'), 
        ('0022', '----', '6e400002-b5a3-f393-e0a9-e50e24dcca9e'), 
        ('0023', 'desc', '0x2902'), 
        ('0024', 'char', '6e400001-b5a3-f393-e0a9-e50e24dcca9e', 'prop=10', '(----N---)'), 
        ('0025', '----', '6e400003-b5a3-f393-e0a9-e50e24dcca9e'), 
        ('0026', 'desc', '0x2902'), 
        ('0027', 'char', '6e400001-b5a3-f393-e0a9-e50e24dcca9e', 'prop=10', '(----N---)'), 
        ('0028', '----', '6e400004-b5a3-f393-e0a9-e50e24dcca9e'), 
        ('0029', 'desc', '0x2902')
    ]
"""