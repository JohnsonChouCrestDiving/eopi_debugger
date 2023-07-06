"""
1. Config the CR1 bluetooth const.
Ex. gatt config, cmd, etc.
2. Implement the CR1 bluetooth function.
"""
from enum import Enum
from interface.interface_worker import  GenericWorker, do_in_thread
from common.convert import Data_convertor as cov
import logging
import time
import os
worker = GenericWorker()
cov = cov()
do_in_thread = do_in_thread(worker)
logger = logging.getLogger('CR1_bt_define')

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

class fw_update():
    def __init__(self, fw_file_path: str, debug: bool = False):
        self._ble = worker.ble
        self.OTA_PKT_DATA_MAX_LEN = 230

        self.file_path = fw_file_path
        self._debug = debug

    @do_in_thread
    def start(self):
        try:
            time_start = time.time()
            self._openedFile = open(self.file_path, 'rb')
            self._fileSize = os.stat(self.file_path).st_size

            if (self._fileSize == 0):
                logger.warning('Open file failed, file path: %s, file size = 0 byte', self.file_path)
                self._openedFile.close()
                err_code = 'OPEN FILE ERR'
            elif (self._send_FW_header() == False):
                logger.error('Send FW header failed, file size = %d bytes.', self._fileSize)
                self._openedFile.close()
                err_code = 'FW HEADER ERR'
            else:
                if (self._send_FW_data() == False):
                    logger.error('Send FW data failed, file size = %d bytes.', self._fileSize)
                    self._openedFile.close()
                    err_code = 'FW DATA ERR'
                elif (self._send_verify_cmd() == False):
                    logger.error('Send verify cmd failed, file size = %d bytes.', self._fileSize)
                    self._openedFile.close()
                    err_code = 'VERIFY FW ERR'
                else:
                    self._send_reset_cmd()
                    logger.info('Exit start_OTA_update')
                    self._openedFile.close()
                    err_code = 'FW UPDATE SUCC'
            time_end = time.time()
            logger.info('FW update time: %f sec', time_end - time_start)
            return err_code
        except Exception as e:
            logger.error('!!!!!!start_OTA_update() Error !!!!!!, Exception: %s', e)
            
    @do_in_thread
    def _send_OTA_packet(self) -> bool:
        self._packet = list()
        self._data_buf = bytearray([])
        rtn = True

        if eAmotaCommand.AMOTA_CMD_FW_DATA.value == self._data_type:
            self._reply = []
            next_packet_start_idx = 0 # Point to the first byte of the next packet.
            packet_serial_number = 0
            while next_packet_start_idx < len(self._data_will_be_send):
                self._split_data(next_packet_start_idx)
                self._generate_pkt()
                self._send_pkt()
                packet_serial_number += 1
                next_packet_start_idx += len(self._data_buf)
                logger.info(
                    'Number %d packet, Send data %d bytes, rest %d bytes.', 
                    packet_serial_number, 
                    len(self._data_buf), 
                    len(self._data_will_be_send) - next_packet_start_idx
                )
                if self._debug: 
                    if self._decode_reply_cmd():
                        continue
                    else:
                        rtn = False
                        break
        else:
            self._data_buf = self._data_will_be_send
            self._generate_pkt()
            self._send_pkt()
            rtn = self._decode_reply_cmd()

        return rtn

    @do_in_thread
    def _send_FW_header(self) -> bool:
        fw_header_read = bytearray([0]*48) # hearder size 固定是 48 bytes
        fw_header_read = self._openedFile.read(48)
        
        if len(fw_header_read) < 48: # bin file for update < 48 bytes
            logger.warning('Invalid packed firmware length.')
            return False
        
        self._fileSize = ((fw_header_read[11] & 255) << 24) + ((fw_header_read[10] & 255) << 16) + ((fw_header_read[9] & 255) << 8) + (fw_header_read[8] & 255)
        logger.info('File size = ' + str(self._fileSize) + '.')
        logger.debug(f'Fw header size = {len(fw_header_read)} bytes.')
        # print('Send fw header ' , fw_header_read, '.')
        self._data_type = eAmotaCommand.AMOTA_CMD_FW_HEADER.value
        self._data_will_be_send = fw_header_read
        if self._send_OTA_packet():
            logger.info('Send firmware header success.')
            return True
        
        return False
    
    @do_in_thread
    def _send_FW_data(self) -> bool:
        fw_data_read = bytearray([])
        self._openedFile.seek(48) # skip header
        fw_data_read = self._openedFile.read(self._fileSize)

        logger.debug('data size = %d bytes.', len(fw_data_read))
        if len(fw_data_read) < self._fileSize: # data actually size < hearder recorded's
            return False

        self._data_type = eAmotaCommand.AMOTA_CMD_FW_DATA.value
        self._data_will_be_send = fw_data_read
        if self._send_OTA_packet():
            logger.info('Send firmware data complete.')
            return True
        
        return False
    
    @do_in_thread
    def _send_verify_cmd(self) -> bool:
        logger.info('Send firmware verify cmd.')
        self._data_type = eAmotaCommand.AMOTA_CMD_FW_VERIFY.value
        self._data_will_be_send = bytearray([])
        if self._send_OTA_packet():
            return True
        
    @do_in_thread
    def _send_reset_cmd(self) -> bool:
        logger.info('Send firmware reset cmd.')
        self._data_type = eAmotaCommand.AMOTA_CMD_FW_RESET.value
        self._data_will_be_send = bytearray([])
        if self._send_OTA_packet():
            return True
            
    def _decode_reply_cmd(self):
        try:
            # [length*2u, cmd*1u, status*1u, data:0~4u]
            error_code = self._reply[0]['data']['value'][3]
            
            if eAmotaStatus.AMOTA_STATUS_SUCCESS.value == error_code:
                logger.info('Send packet success.')
                time.sleep(0.01)
                return True
            elif eAmotaStatus.AMOTA_STATUS_CRC_ERROR.value == error_code:
                logger.error('Send packet failed, status = AMOTA_STATUS_CRC_ERROR.')
                return False
            elif eAmotaStatus.AMOTA_STATUS_INVALID_HEADER_INFO.value == error_code:
                logger.error('Send packet failed, status = AMOTA_STATUS_INVALID_HEADER_INFO.')
                return False
            elif eAmotaStatus.AMOTA_STATUS_INVALID_PKT_LENGTH.value == error_code:
                logger.error('Send packet failed, status = AMOTA_STATUS_INVALID_PACKET_LENGTH.')
                return False
            elif eAmotaStatus.AMOTA_STATUS_INSUFFICIENT_BUFFER.value == error_code:
                logger.error('Send packet failed, status = AMOTA_STATUS_INSUFFICIENT_BUFFER.')
                return False
            elif eAmotaStatus.AMOTA_STATUS_INSUFFICIENT_FLASH.value == error_code:
                logger.error('Send packet failed, status = AMOTA_STATUS_INSUFFICIENT_FLASH.')
                return False
            elif eAmotaStatus.AMOTA_STATUS_UNKNOWN_ERROR.value == error_code:
                logger.error('Send packet failed, status = AMOTA_STATUS_UNKNOWN_ERROR.')
                return False
            elif eAmotaStatus.AMOTA_STATUS_FLASH_WRITE_ERROR.value == error_code:
                logger.error('Send packet failed, status = AMOTA_STATUS_FLASH_WRITE_ERROR.')
                return False
            elif eAmotaStatus.AMOTA_STATUS_MAX.value == error_code:
                logger.error('Send packet failed, status = AMOTA_STATUS_MAX.')
                return False
        except:
            logger.warning('No reply or reply out time.')
    
    def _generate_pkt(self):
        self._packet.clear()
        self._packet.extend(cov.swap_endian(cov.i16_to_u8_list(len(self._data_buf) + 4)))   # length*2u
        self._packet.append(self._data_type)                                                # header:OTA_cmd*1u
        self._packet.extend(self._data_buf)                                                 # data:0~64u
        self._packet.extend(cov.swap_endian(cov.i32_to_u8_list(                             # checksum*4u
            self._ble.get_checksum_crc32(self._data_buf)
        )))
    
    @do_in_thread
    def _send_pkt(self):
        if (self._data_type == eAmotaCommand.AMOTA_CMD_FW_DATA.value and not self._debug):
            self._ble.write(GATT_CONFIG['ota_rx'][0], self._packet)
            time.sleep(0.04)
        else:
            self._reply = self._ble.read(GATT_CONFIG['ota_rx'][0], self._packet, 1)
    
    def _split_data(self, start_seek: int):
        if len(self._data_will_be_send) - start_seek > self.OTA_PKT_DATA_MAX_LEN: 
            self._data_buf.clear()
            self._data_buf.extend(
                self._data_will_be_send[start_seek: start_seek + self.OTA_PKT_DATA_MAX_LEN]
            )
        else:
            self._data_buf.clear()
            self._data_buf.extend(self._data_will_be_send[start_seek:])
