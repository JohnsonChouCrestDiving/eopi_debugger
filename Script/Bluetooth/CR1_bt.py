"""
1. Config the CR1 bluetooth const.
Ex. gatt config, cmd, etc.
2. Implement the CR1 bluetooth function.
"""
from enum import Enum
from interface.interface_worker import  GenericWorker, do_in_thread
from page.factory_full_test.msg import NotifyType
from common.convert import Data_convertor as cov
from Error.err_cls import *
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
    'WHERE_MY_WATCH'    :{'cmd': [0xA0, 0x00, 0x00, 0x00, 0xFF],    'read_num': 1},
    'GET_FW_VER'        :{'cmd': [0xA0, 0x01, 0x01, 0x5A],          'read_num': 1},
    'SN'                :{'cmd': [0xA0, 0x02, 0x01, 0x65],          'read_num': 1},
    'CHECK_ALIVE'       :{'cmd': [0xA0, 0x04, 0x01, 0x1B],          'read_num': 1},
    # EOPI TEST
    'GET_TEMPERATURE'   :{'cmd': [0xD0, 0x03, 0x01, 0x17],          'read_num': 1},
    'GET_PRESSURE'      :{'cmd': [0xD0, 0x04, 0x01, 0x7C],          'read_num': 1},
    'GET_BATTERY_VOLT'  :{'cmd': [0xD0, 0x0A, 0x01, 0xAA],          'read_num': 1},
    'TEST_RTC_IC'       :{'cmd': [0xD0, 0x0B, 0x01, 0xBF],          'read_num': 1},
    'GET_BUILD_TIME'    :{'cmd': [0xD0, 0x0D, 0x01, 0xC1],          'read_num': 1},
    'TEST_FLASH_IC'     :{'cmd': [0xD0, 0x0F, 0x01, 0xEB],          'read_num': 1},
    'SET_SN'            :{'cmd': [0xD0, 0x10, 0x00],                'read_num': 0},
    'GET_SN'            :{'cmd': [0xD0, 0x10, 0x01, 0x7F],          'read_num': 1},
    'CAL_PRESSURE'      :{'cmd': [0xD0, 0x11, 0x00],                'read_num': 1},
    'LOG_READOUT'       :{'cmd': [0xD0, 0x12, 0x01, 0x55],          'read_num': 1},
    'W_TEST_RESULT'     :{'cmd': [0xD0, 0x12, 0x00],                'read_num': 0},
    'TRUE_READ_FLAG'    :{'cmd': [0xD0, 0x13, 0x00, 0x01, 0xD5],    'read_num': 1},
    'FALSE_READ_FLAG'   :{'cmd': [0xD0, 0x13, 0x00, 0x00, 0xD2],    'read_num': 1},
    'GET_READ_FLAG'     :{'cmd': [0xD0, 0x13, 0x01, 0x40],          'read_num': 1},
    'GET_P_AFTER_CAL'   :{'cmd': [0xD0, 0x14, 0x01, 0x2B],          'read_num': 1},
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
    FLASH_NO_ERR            = 0
    FLASH_ERR_COMMUNICATION = 1
    FLASH_ERR_WRITE         = 2
    FLASH_ERR_READ          = 3
    FLASH_ERR_ID            = 4

class test():
    def __init__(self):
        self._ble = worker.ble
        self._test_data = {}

    @do_in_thread
    def start(self):
        self._verify_battery_volt()
        self._test_rtc_ic()
        self._test_flash_ic()
        self._verify_temperature()
        self._verify_pressure()
        self._write_test_log()
        self._gen_data()
        return True

    @do_in_thread
    def get_result_data(self):
        """
        {
            'battery_voltage': (int, 'err_msg'),
            'rtc': (0 ~ 2, 'err_msg'),
            'flash': (0 ~ 4, 'err_msg'),
            'temperature': (uint8, 'err_msg'),
            'pressure': (uint16, 'err_msg')
        }
        """
        return self._test_data
    
    @do_in_thread
    def _gen_data(self):
        self._test_data['battery_voltage'] = (
            self._battery_volt, 
            'Pass' if self._isVInRange else 'Out of range'
            )
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
    def _verify_battery_volt(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['GET_BATTERY_VOLT']['cmd'],
            ACTION['GET_BATTERY_VOLT']['read_num']
        )
        if len(res) == 0:
            raise serverNoResponse('TEST1 FAIL')
        self._battery_volt = cov.uint16_to_int(cov.swap_endian(res[0]['data']['value'][3:5])) # mV
        self._isVInRange = 2400 < self._battery_volt and self._battery_volt < 3300

    @do_in_thread
    def _test_rtc_ic(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['TEST_RTC_IC']['cmd'],
            ACTION['TEST_RTC_IC']['read_num']
        )
        if len(res) == 0:
            raise serverNoResponse('TEST2 FAIL')
        self._rtc_rslt = res[0]['data']['value'][3]

    @do_in_thread
    def _test_flash_ic(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['TEST_FLASH_IC']['cmd'],
            ACTION['TEST_FLASH_IC']['read_num']
        )
        if len(res) == 0:
            raise serverNoResponse('TEST3 FAIL')
        self._flash_rslt = res[0]['data']['value'][3]

    @do_in_thread
    def _verify_pressure(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['GET_P_AFTER_CAL']['cmd'],
            ACTION['GET_P_AFTER_CAL']['read_num']
        )
        if len(res) == 0:
            raise serverNoResponse('TEST5 FAIL')
        print(cov.swap_endian(res[0]['data']['value'][3:7]))
        self._pressure = cov.u8list_2_float(cov.swap_endian(res[0]['data']['value'][3:7]))
        self._pressure = round(self._pressure, 1)
        self._isPInRange = 900 < self._pressure and self._pressure < 1100

    @do_in_thread
    def _verify_temperature(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['GET_TEMPERATURE']['cmd'],
            ACTION['GET_TEMPERATURE']['read_num']
        )
        if len(res) == 0:
            raise serverNoResponse('TEST4 FAIL')
        self._temperature = cov.uint16_to_int(cov.swap_endian(res[0]['data']['value'][3:5]))
        self._isTInRange = 10 < self._temperature and self._temperature < 30

    @do_in_thread
    def _write_test_log(self):
        data = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        data.extend(cov.i16_to_u8_list(self._battery_volt))
        data.append(self._rtc_rslt)
        data.append(self._flash_rslt)
        data.extend(cov.i16_to_u8_list(int(round(self._pressure))))
        data.extend(cov.i16_to_u8_list(self._temperature))
        pkt_no_checksum = ACTION['W_TEST_RESULT']['cmd'] + data
        pkt = pkt_no_checksum + [self._ble.get_checksum(pkt_no_checksum)]
        self._ble.write(GATT_CONFIG['app_rx'][0], pkt)

class calibrate_pressure():
    """
    Module for calibrating pressure
    """
    def __init__(self, real_pressure: float):
        self._ble = worker.ble
        self.pressure = real_pressure

    @do_in_thread
    def start(self):
        """
        @return: p(before cal), p(after cal), p(cal factor)
        """
        before, after, factor = self._calibrate_pSensor()
        self._set_read_flag_false()
        return before, after, factor
    
    @do_in_thread
    def _calibrate_pSensor(self):
        pkt_no_checksum = ACTION['CAL_PRESSURE']['cmd'] + cov.swap_endian(cov.float_2_u8list(self.pressure))
        pkt_no_checksum.append(self._ble.get_checksum(pkt_no_checksum))
        pkt = pkt_no_checksum
        res = self._ble.read(GATT_CONFIG['app_rx'][0], pkt, ACTION['CAL_PRESSURE']['read_num'])
        if len(res) == 0:
            raise serverNoResponse('RECIVE FAIL')
        p_factor = round(cov.u8list_2_float(cov.swap_endian(res[0]['data']['value'][3:7])), 1)
        p_before = round(cov.u8list_2_float(cov.swap_endian(res[0]['data']['value'][7:11])), 1)
        p_after = round(cov.u8list_2_float(cov.swap_endian(res[0]['data']['value'][11:15])), 1)
        return  p_before, p_after, p_factor
    
    @do_in_thread
    def _set_read_flag_false(self):
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0], 
            ACTION['FALSE_READ_FLAG']['cmd'], 
            ACTION['FALSE_READ_FLAG']['read_num']
        )
        if len(res) == 0:
            raise serverNoResponse('RECIVE FAIL, Set watch log read out flag fail')
        if (res[0]['data']['value'][3]!=0):
            raise serverNoResponse('Set watch log read out flag fail')

class fw_update():
    """
    Module for OTA firmware update
    """
    def __init__(self, fw_file_path: str, debug: bool = False):
        self._ble = worker.ble
        self._show_percent_cnt = 0
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
                worker.message.emit([
                    NotifyType.ACTION.value,
                    f'otaProgressBar{round(next_packet_start_idx/len(self._data_will_be_send)*100)}'
                ])
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
                time.sleep(0.02)
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
        
        self._fileSize = (
            ((fw_header_read[11] & 255) << 24) 
            + ((fw_header_read[10] & 255) << 16) 
            + ((fw_header_read[9] & 255) << 8) 
            + (fw_header_read[8] & 255)
        )
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
        return self._send_OTA_packet()
        
    @do_in_thread
    def _send_reset_cmd(self) -> bool:
        logger.info('Send firmware reset cmd.')
        self._data_type = eAmotaCommand.AMOTA_CMD_FW_RESET.value
        self._data_will_be_send = bytearray([])
        return self._send_OTA_packet()
            
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
            return False
    
    def _generate_pkt(self):
        self._packet.clear()
        self._packet.extend(cov.swap_endian(cov.i16_to_u8_list(len(self._data_buf) + 4)))   # length*2u
        self._packet.append(self._data_type)                                                # header:OTA_cmd*1u
        self._packet.extend(self._data_buf)                                                 # data:0~230u
        self._packet.extend(cov.swap_endian(cov.i32_to_u8_list(                             # checksum*4u
            self._ble.get_checksum_crc32(self._data_buf)
        )))
    
    @do_in_thread
    def _send_pkt(self):
        if (self._data_type == eAmotaCommand.AMOTA_CMD_FW_DATA.value and not self._debug):
            self._ble.write(GATT_CONFIG['ota_rx'][0], self._packet)
            time.sleep(0.04)
        elif (self._data_type == eAmotaCommand.AMOTA_CMD_FW_DATA.value and not self._debug):
            self._reply = self._ble.read(GATT_CONFIG['ota_rx'][0], self._packet, 1)
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

class device():
    def __init__(self):
        self._ble = worker.ble
    
    @do_in_thread
    def set_sn(self, sn: str):
        sn_list = [0]*32
        sn_list[0:len(sn)] = cov.ASCII_to_u8_list(sn)
        pkt_no_checksum = ACTION['SET_SN']['cmd'] + sn_list
        pkt_no_checksum.append(self._ble.get_checksum(pkt_no_checksum))
        pkt = pkt_no_checksum
        self._ble.write(GATT_CONFIG['app_rx'][0], pkt)

    @do_in_thread
    def get_sn(self):
        try:
            sn = cov.intList_to_ASCII(
                self._ble.read(
                    GATT_CONFIG['app_rx'][0], 
                    ACTION['GET_SN']['cmd'], 
                    ACTION['GET_SN']['read_num']
                )[0]['data']['value'][3:-1]
            )
            return sn.rstrip('\x00')
        except:
            return '----'
    
    @do_in_thread
    def check_communicable(self):
        try:
            return 'Hello' == cov.intList_to_ASCII(
                self._ble.read(
                    GATT_CONFIG['app_rx'][0], 
                    ACTION['CHECK_ALIVE']['cmd'], 
                    ACTION['CHECK_ALIVE']['read_num']
                )[0]['data']['value'][3:-1]
            )
        except:
            return False
        
    @do_in_thread
    def find_watch(self):
        try:
            res = self._ble.read(
                GATT_CONFIG['app_rx'][0], 
                ACTION['WHERE_MY_WATCH']['cmd'], 
                ACTION['WHERE_MY_WATCH']['read_num']
            )
            rtn = res[0]['data']['value'][3:]
        except:
            rtn = []
        return rtn
    
    @do_in_thread
    def subscribe_app_uuid(self):
        self._ble.subscribe(GATT_CONFIG['app_rx'][0], GATT_CONFIG['app_rx'][1])
        self._ble.subscribe(GATT_CONFIG['app_tx'][0], GATT_CONFIG['app_tx'][1])
        self._ble.enable_all_notify()
    
    @do_in_thread
    def subscribe_ota_uuid(self):
        self._ble.subscribe(GATT_CONFIG['ota_rx'][0], GATT_CONFIG['ota_rx'][1])
        self._ble.subscribe(GATT_CONFIG['ota_tx'][0], GATT_CONFIG['ota_tx'][1])
        self._ble.enable_all_notify()

    def get_fw_ver(self):
        try:
            return cov.intList_to_ASCII(
                self._ble.read(
                    GATT_CONFIG['app_rx'][0], 
                    ACTION['GET_FW_VER']['cmd'], 
                    ACTION['GET_FW_VER']['read_num']
                )[0]['data']['value'][3:-1]
            )
        except:
            return '----'
    
    def get_build_time(self):
        try:
            return cov.intList_to_ASCII(
                self._ble.read(
                    GATT_CONFIG['app_rx'][0], 
                    ACTION['GET_BUILD_TIME']['cmd'], 
                    ACTION['GET_BUILD_TIME']['read_num']
                )[0]['data']['value'][3:-1]
            )
        except:
            return '--- 0 0000, 00:00:00'
        
    def get_battery_volt(self):
        try:
            return cov.uint16_to_int(
                cov.swap_endian(
                    self._ble.read(
                        GATT_CONFIG['app_rx'][0],
                        ACTION['GET_BATTERY_VOLT']['cmd'],
                        ACTION['GET_BATTERY_VOLT']['read_num']
                    )[0]['data']['value'][3:5]  # mV
                )
            )
        except:
            return '----'

class log_readout():
    def __init__(self):
        self._ble = worker.ble
        self._factory_calibration_xt = {
            'is_logreadout' :False,
            'p_cal_offset' :0,
            'p_cal_before' :0,
            'p_cal_after' :0,
            'battery_voltage_test' :0,
            'rtc_test' :0,
            'flash_test' :0,
            'pressure_test' :0,
            'temperature_test' :0,
        }
        self._all_test_result = {}

    def start(self):
        data = self._read_test_log()
        self._decode_test_log_pkt_data(data)
        self._gen_inf()
        return True
    
    def get_all_test_result(self):
        """
        return = {
            'cal_pressure_offset': (float, '--'),
            'cal_pressure_before': (float, '--'),
            'cal_pressure_after': (float, '--'),
            'battery_voltage': (int, 'err_msg'),
            'rtc': (0 ~ 2, 'err_msg'),
            'flash': (0 ~ 4, 'err_msg'),
            'temperature': (uint8, 'err_msg'),
            'pressure': (uint16, 'err_msg')
        }
        """
        return self._all_test_result

    @do_in_thread
    def _read_test_log(self):
        """
        return:[
            pressure_calibrate_factor: 4u(float),
            pressure_calibrate_before: 4u(float),
            pressure_calibrate_after: 4u(float),
            voltage_test: 2u(uint16_t),
            rtc_test: 1u(uint8_t),
            flash_test: 1u(uint8_t),
            psensor_test: 2u(uint16_t),
            temperature_test: 2u(uint16_t)
        ]
        """
        res = self._ble.read(
            GATT_CONFIG['app_rx'][0],
            ACTION['LOG_READOUT']['cmd'],
            ACTION['LOG_READOUT']['read_num']
        )
        if len(res) == 0:
            raise serverNoResponse('RECIVE FAIL')
        if (self._ble.read(
                GATT_CONFIG['app_rx'][0], 
                ACTION['TRUE_READ_FLAG']['cmd'], 
                ACTION['TRUE_READ_FLAG']['read_num']
            )[0]['data']['value'][3] != 1):
            raise serverNoResponse('Set watch log read out flag fail')
        return res[0]['data']['value'][3:-1]

    def _decode_test_log_pkt_data(self, data:list):
        try:
            self._factory_calibration_xt['is_logreadout'] = data[0]
            self._factory_calibration_xt['p_cal_offset'] = round(cov.u8list_2_float(cov.swap_endian(data[1:5])), 1)
            self._factory_calibration_xt['p_cal_before'] = round(cov.u8list_2_float(cov.swap_endian(data[5:9])), 1)
            self._factory_calibration_xt['p_cal_after'] = round(cov.u8list_2_float(cov.swap_endian(data[9:13])), 1)
            self._factory_calibration_xt['battery_voltage_test'] = cov.uint16_to_int(cov.swap_endian(data[13:15]))
            self._factory_calibration_xt['rtc_test'] = data[15]
            self._factory_calibration_xt['flash_test'] = data[16]
            self._factory_calibration_xt['pressure_test'] = cov.uint16_to_int(cov.swap_endian(data[17:19]))
            self._factory_calibration_xt['temperature_test'] = cov.uint16_to_int(cov.swap_endian(data[19:21]))
        except:
            raise Exception

    def _gen_inf(self):
        self._isVInRange = (
            2400 < self._factory_calibration_xt['battery_voltage_test'] 
            and self._factory_calibration_xt['battery_voltage_test'] < 3300
        )
        self._isTInRange = (
            10 < self._factory_calibration_xt['temperature_test'] 
            and self._factory_calibration_xt['temperature_test'] < 30
        )
        self._isPInRange = (
            900 < self._factory_calibration_xt['pressure_test'] 
            and self._factory_calibration_xt['pressure_test'] < 1100
        )

        self._all_test_result['cal_pressure_offset'] = (
            self._factory_calibration_xt['p_cal_offset'], '--'
        )
        self._all_test_result['cal_pressure_before'] = (
            self._factory_calibration_xt['p_cal_before'], '--'
        )
        self._all_test_result['cal_pressure_after'] = (
            self._factory_calibration_xt['p_cal_after'], '--'
        )
        self._all_test_result['battery_voltage'] = (
            self._factory_calibration_xt['battery_voltage_test'], 
            'Pass' if self._isVInRange else 'Out of range'
        )
        self._all_test_result['rtc'] = (
            self._factory_calibration_xt['rtc_test'], 
            'Pass' 
            if self._factory_calibration_xt['rtc_test'] == 0 else 
            rtcErrCode(self._factory_calibration_xt['rtc_test']).name
        )
        self._all_test_result['flash'] = (
            self._factory_calibration_xt['flash_test'], 
            'Pass' 
            if self._factory_calibration_xt['flash_test'] == 0 else 
            flashErrCode(self._factory_calibration_xt['flash_test']).name
        )
        self._all_test_result['temperature'] = (
            self._factory_calibration_xt['temperature_test'],
            'Pass' if self._isTInRange else 'Out of range'
        )
        self._all_test_result['pressure'] = (
            self._factory_calibration_xt['pressure_test'],
            'Pass' if self._isPInRange else 'Out of range'
        )

    def is_read_out(self):
        """
        @return 0: not read out, 1: read out
        """
        return (
            self._ble.read(
                GATT_CONFIG['app_rx'][0], 
                ACTION['GET_READ_FLAG']['cmd'], 
                ACTION['GET_READ_FLAG']['read_num']
            )[0]['data']['value'][3]
        )
