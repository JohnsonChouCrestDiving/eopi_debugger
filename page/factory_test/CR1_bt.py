"""
1. Config the CR1 bluetooth const.
Ex. gatt config, cmd, etc.
2. Implement the CR1 bluetooth function.
"""
from enum import Enum
from interface.interface_worker import  GenericWorker, do_in_thread
from common.convert import Data_convertor as cov
worker = GenericWorker()
cov = cov()
do_in_thread = do_in_thread(worker)

GATT_CONFIG = {
    'app_rx' : ('00002760-08C2-11E1-9073-0E8AC72E2012', True ),
    'app_tx' : ('00002760-08C2-11E1-9073-0E8AC72E2013', False),
    'ota_rx' : ('00002760-08C2-11E1-9073-0E8AC72E0001', False),
    'ota_tx' : ('00002760-08C2-11E1-9073-0E8AC72E0002', False),
    'ota_ack': ('00002760-08C2-11E1-9073-0E8AC72E0003', False),
    'dtp_rx' : ('00002760-08C2-11E1-9073-0E8AC72E0011', False),
    'dtp_tx' : ('00002760-08C2-11E1-9073-0E8AC72E0012', False),
    'dtp_ack': ('00002760-08C2-11E1-9073-0E8AC72E0013', False),
}

ACTION = {
    # DEVICE
    'WHERE_MY_WATCH'    :{'cmd': [0xA0, 0x00, 0x00, 0x00, 0xFF], 'read_num': 1},
    # EOPI TEST
    'GET_TEMPERATURE'   :{'cmd': [0xD0, 0x03, 0x01, 0x17],       'read_num': 1},
    'GET_PRESSURE'      :{'cmd': [0xD0, 0x04, 0x01, 0x7C],       'read_num': 1},
    'GET_BATTERY_VOLT'  :{'cmd': [0xD0, 0x0A, 0x01, 0xAA],       'read_num': 1},
    'TEST_RTC_IC'       :{'cmd': [0xD0, 0x0B, 0x01, 0xBF],       'read_num': 1},
    'TEST_FLASH_IC'     :{'cmd': [0xD0, 0x0F, 0x01, 0xEB],       'read_num': 1},
}

class eAmotaCommand(Enum):
    AMOTA_CMD_UNKNOWN   = 0
    AMOTA_CMD_FW_HEADER = 1
    AMOTA_CMD_FW_DATA   = 2
    AMOTA_CMD_FW_VERIFY = 3
    AMOTA_CMD_FW_RESET  = 4
    AMOTA_CMD_MAX       = 5

class eAmotaStatus(Enum):
    AMOTA_STATUS_SUCCESS                = 0
    AMOTA_STATUS_CRC_ERROR              = 1
    AMOTA_STATUS_INVALID_HEADER_INFO    = 2
    AMOTA_STATUS_INVALID_PKT_LENGTH     = 3
    AMOTA_STATUS_INSUFFICIENT_BUFFER    = 4
    AMOTA_STATUS_INSUFFICIENT_FLASH     = 5
    AMOTA_STATUS_UNKNOWN_ERROR          = 6
    AMOTA_STATUS_FLASH_WRITE_ERROR      = 7
    AMOTA_STATUS_MAX                    = 8

class rtcErrCode(Enum):
    NO_ERR              = 0
    ERR_COMMUNICATION   = 1
    ERR_ID              = 2

class flashErrCode(Enum):
    NO_ERR              = 0
    ERR_COMMUNICATION   = 1
    ERR_ID              = 2

class test():
    def __init__(self):
        self._ble = worker.ble
        self._test_data = {}

    @do_in_thread
    def start(self):
        self._test_rtc_ic()
        self._test_flash_ic()
        self._verify_temperature()
        self._verify_pressure()
        self._gen_data()
        return True

    @do_in_thread
    def get_result_data(self):
        """
        {
            'rtc': (0 ~ 2, 'err_msg'),
            'flash': (0 ~ 2, 'err_msg'),
            'temperature': (uint8, 'err_msg'),
            'pressure': (uint16, 'err_msg')
        }
        """
        return self._test_data
    
    @do_in_thread
    def _gen_data(self):
        self._test_data['rtc'] = (
            self._rtc_rslt, 
            'Pass' if self._rtc_rslt == 0 else rtcErrCode(self._rtc_rslt).name
        )
        self._test_data['flash'] = (
            self._flash_rslt, 
            'Pass' if self._flash_rslt == 0 else flashErrCode(self._flash_rslt).name
        )
        self._test_data['temperature'] = (
            self._temperature,
            'Pass' if self._isTInRange else 'Out of range'
        )
        self._test_data['pressure'] = (
            self._pressure,
            'Pass' if self._isPInRange else 'Out of range'
        )

    @do_in_thread
    def _test_rtc_ic(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['TEST_RTC_IC']['cmd'],
            ACTION['TEST_RTC_IC']['read_num']
        )
        self._rtc_rslt = res[0]['data']['value'][3]

    @do_in_thread
    def _test_flash_ic(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['TEST_FLASH_IC']['cmd'],
            ACTION['TEST_FLASH_IC']['read_num']
        )
        self._flash_rslt = res[0]['data']['value'][3]

    @do_in_thread
    def _verify_pressure(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['GET_PRESSURE']['cmd'],
            ACTION['GET_PRESSURE']['read_num']
        )
        self._pressure = cov.uint16_to_int(res[0]['data']['value'][3:5])
        self._isPInRange = 900 < self._pressure and self._pressure < 1100

    @do_in_thread
    def _verify_temperature(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['GET_TEMPERATURE']['cmd'],
            ACTION['GET_TEMPERATURE']['read_num']
        )
        self._temperature = cov.uint16_to_int(res[0]['data']['value'][3:5])
        self._isTInRange = 10 < self._temperature and self._temperature < 30
        