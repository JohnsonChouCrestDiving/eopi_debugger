#standard library
import sys
import os
import time
import random
import enum
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from interface.bluetooth.bluetooth import Bluetooth_LE
from common.convert import Data_convertor as cov
from common.UI_object import Right_click_menu_generator, TextBrowser_msg_handler
from common.config import Config_creator
# from log.logger import loggers
import logging
logger = logging.getLogger('bluetooth')

#sub-module
if __name__ == '__main__':
    from UI_ble_command import Ui_CR1_ble_command
else:
    from .UI_ble_command import Ui_CR1_ble_command
    
address = 'C2:5E:51:CF:C5:2E'
address2 = 'C9:AE:EB:DC:4D:FB'
address3 = 'C3:B4:89:3C:FA:14'
address4 = 'E8:E9:2E:EC:9E:8A'      # apollo3p

uuid_app_rx = '00002760-08C2-11E1-9073-0E8AC72E2012'
uuid_app_tx = '00002760-08C2-11E1-9073-0E8AC72E2013'
uuid_ota_rx = '00002760-08C2-11E1-9073-0E8AC72E0001'
uuid_ota_tx = '00002760-08C2-11E1-9073-0E8AC72E0002'
uuid_ota_ack = '00002760-08C2-11E1-9073-0E8AC72E0003'
uuid_dtp_rx = '00002760-08C2-11E1-9073-0E8AC72E0011'
uuid_dtp_tx = '00002760-08C2-11E1-9073-0E8AC72E0012'
uuid_dtp_ack = '00002760-08C2-11E1-9073-0E8AC72E0013'

OTA_PKT_DATA_MAX_LEN = 230 # It requires larger than 48, because header needs sending in one packet
class eAmotaCommand(enum.Enum):
    AMOTA_CMD_UNKNOWN   = 0
    AMOTA_CMD_FW_HEADER = 1
    AMOTA_CMD_FW_DATA   = 2
    AMOTA_CMD_FW_VERIFY = 3
    AMOTA_CMD_FW_RESET  = 4
    AMOTA_CMD_MAX       = 5
class eAmotaStatus(enum.Enum):
    AMOTA_STATUS_SUCCESS                = 0
    AMOTA_STATUS_CRC_ERROR              = 1
    AMOTA_STATUS_INVALID_HEADER_INFO    = 2
    AMOTA_STATUS_INVALID_PKT_LENGTH     = 3
    AMOTA_STATUS_INSUFFICIENT_BUFFER    = 4
    AMOTA_STATUS_INSUFFICIENT_FLASH     = 5
    AMOTA_STATUS_UNKNOWN_ERROR          = 6
    AMOTA_STATUS_FLASH_WRITE_ERROR      = 7
    AMOTA_STATUS_MAX                    = 8

cov = cov()
worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class cr1_ble_command(QWidget, Ui_CR1_ble_command):
    
    def __init__(self):
        super(cr1_ble_command, self).__init__()
        self.setupUi(self)

        self.config = Config_creator('cr1_ble_command')
        self.config_path = self.config.get_path()
        self.ble = worker.ble
        self.handle = None
        self.ble.rx_data.connect(self.show_reply)
        self.bt_device_list = {}
        self.__openedFile = None
        self.__fileSize = 0

        self.scan_rssi_filter = -50

        # self.cmd_read_tide_pushButton.clicked.connect(self.foo_read_tide_info)
        # self.cmd_write_tide_pushButton.clicked.connect(self.foo_send_tide_info)
        self.connect_pushButton.clicked.connect(self.connect_ble_device)
        self.disconnect_pushButton.clicked.connect(self.disconnect_ble_device)
        self.show_characteristic_pushButton.clicked.connect(self.dive_sim)
        self.scan_device_pushButton.clicked.connect(self.scan_device)
        self.ble_address_lineEdit.setInputMask('HH:HH:HH:HH:HH:HH')
        self.Btn_selectFile.clicked.connect(self.select_file)
        self.Btn_updataFw.clicked.connect(self.start_OTA_update)

        self.selectPSensor_cb.currentIndexChanged.connect(self.change_current_pressure_sensor)
        self.selectPSensor_cb.addItems(['TEST_PRESSURE_SENSOR', 'MS5837_30BA', 'NONE_OF_THIS_SENSOR'])
        self.lineEdit_Pressure.setInputMask('9999')
        self.lineEdit_Temp.setInputMask('99')
        self.lineEdit_Pressure.setText('0000')
        self.lineEdit_Temp.setText('00')
        self.Btn_setPressure.clicked.connect(self.set_pSensor_pressure)
        self.Btn_setTemp.clicked.connect(self.set_pSensor_temperature)

        if __name__ == '__main__':
            worker.UI.connect(self.set_UI)

    @do_in_thread
    def connect_ble_device(self):
        # try:
        if 1:
            if self.ble.client == None:
                self.ble.select_interface(2)
            self.ble.add_subscribe(uuid_app_rx, True)
            self.ble.add_subscribe(uuid_app_tx, False)
            self.ble.add_subscribe(uuid_ota_rx, False)
            self.ble.add_subscribe(uuid_ota_tx, False)
            self.ble.connect(address4)
            # self.handle = self.ble.get_handle()
            self.ble.enable_all_notify()
        # except:
        #     pass

    @do_in_thread
    def disconnect_ble_device(self):
        self.ble.disconnect()

    @do_in_thread
    def scan_device(self):
        worker.UI.emit(lambda: self.display_textBrowser.append(f'RSSI filter = {self.scan_rssi_filter}'))
        self.bt_device_list = {}
        if self.ble.client == None:
            self.ble.select_interface(1)
        # self.ble.write('E0262760-08C2-11E1-9073-0E8AC72E2A23', [0x00])
        self.ble.scan(timeout=5, scan_cb=self.store_scan_data)
        self.display_scan_data()

    @do_in_thread
    def read_test(self):
        a = self.ble.read(uuid_app_rx, [0xa0, 0x00, 0x00, 0x00, 0xff], 1)
        print(a)
    
    @do_in_thread
    def dive_sim(self):
        depth = 1000
        depth_step = 302
        time.sleep(0.5)
        self.set_pSensor(0x00)
        time.sleep(1)
        self.set_test_pressure_value(depth)
        cmd = [0xd0, 0x05, 0x01]
        cmd.append(self.ble.get_checksum(cmd))
        init_status = self.ble.read(uuid_app_rx, cmd, 20)
        worker.UI.emit(lambda: self.display_textBrowser.append(f'{init_status}\n'))


        for i in range(1, 6):
            time.sleep(2)
            depth+=depth_step
            self.set_test_pressure_value(depth)
            
            cmd = [0xd0, 0x06, 0x01]
            cmd.append(self.ble.get_checksum(cmd))
            update_status = self.ble.read(uuid_app_rx, cmd, 160)
            worker.UI.emit(lambda: self.display_textBrowser.append(f'{update_status}\n'))

        for i in range(1, 6):
            time.sleep(2)
            depth-=depth_step
            self.set_test_pressure_value(depth)

            cmd = [0xd0, 0x06, 0x01]
            cmd.append(self.ble.get_checksum(cmd))
            update_status = self.ble.read(uuid_app_rx, cmd, 160)
            worker.UI.emit(lambda: self.display_textBrowser.append(f'{update_status}\n'))

        time.sleep(10)
        
        cmd = [0xd0, 0x07, 0x01]
        cmd.append(self.ble.get_checksum(cmd))
        end_status = self.ble.read(uuid_app_rx, cmd, 160)
        worker.UI.emit(lambda: self.display_textBrowser.append(f'{end_status}\n'))


        
    @do_in_thread
    def change_current_pressure_sensor(self):
        # cmd = [0xd0, 0x05, 0x00, self.selectPSensor_cb.currentIndex()]
        # cmd.append(self.ble.get_checksum(cmd))
        # self.ble.write(uuid_app_rx, cmd)
        self.set_pSensor(self.selectPSensor_cb.currentIndex())

    @do_in_thread
    def set_pSensor(self, index):
        cmd = [0xd0, 0x05, 0x00, index]
        cmd.append(self.ble.get_checksum(cmd))
        self.ble.write(uuid_app_rx, cmd)

    @do_in_thread
    def set_pSensor_pressure(self):
        try:
            # to prevent any unexpected value case GUI crash
            value = int(self.lineEdit_Pressure.text())
            self.set_test_pressure_value(value)
        except:
            pass

    @do_in_thread
    def set_test_pressure_value(self, value:int):
        cmd = [0xd0, 0x04, 0x00]
        cmd.extend(cov.swap_endian(cov.i16_to_u8_list(value)))
        cmd.append(self.ble.get_checksum(cmd))
        self.ble.write(uuid_app_rx, cmd)

    @do_in_thread
    def set_pSensor_temperature(self):
        try:
            # to prevent any unexpected value case GUI crash
            value = int(self.lineEdit_Temp.text())
            self.set_test_temperature_value(value)
        except:
            pass

    @do_in_thread
    def set_test_temperature_value(self, value:int):
        cmd = [0xd0, 0x03, 0x00]
        cmd.extend(cov.swap_endian(cov.i16_to_u8_list(value)))
        cmd.append(self.ble.get_checksum(cmd))
        self.ble.write(uuid_app_rx, cmd)

    def display_scan_data(self):
        for addr, datas in self.bt_device_list.items():
            device_name = datas['device_name']
            rssi = datas['rssi']
            worker.UI.emit(lambda addr=addr, device_name=device_name, rssi=rssi: self.display_textBrowser.append(f'Address: {addr}, Name: {device_name}, RSSI: {rssi}'))
            # datas = packet_data.get('connectable_advertisement_packet')
            datas = datas['packet_data']
            if datas != None:
                for key2, value2 in datas.items():
                    worker.UI.emit(lambda key2=key2: self.display_textBrowser.append(f'   {key2}'))
                    for key3, value3 in value2.items():
                        worker.UI.emit(lambda key3=key3, value3=value3: self.display_textBrowser.append(f'       {key3}: {value3}'))
            worker.UI.emit(lambda: self.display_textBrowser.append(f'\n'))

    def store_scan_data(self, msg, a, b):
        for key, value in msg.items():
            device_name = value.name
            address = value.address
            rssi = value.rssi
            packet_data = value.packet_data
            if rssi > self.scan_rssi_filter:
                if address not in self.bt_device_list.keys():
                    print(address, self.bt_device_list.keys())
                    self.bt_device_list[address] = {
                        'device_name': device_name,
                        'rssi': rssi,
                        'packet_data': packet_data
                        }
                else:
                    self.bt_device_list[address]['device_name'] = device_name if device_name != ' ' else self.bt_device_list[address]['device_name']

    def add_checksum(self, list):
        pass

            # if address not in self.bt_device_list.keys() and rssi > self.scan_rssi_filter:
            #     print(f'Device Name: {value.name}, Address: {value.address}, RSSI: {value.rssi}, packet: {value.packet_data}')
            #     self.bt_device_list[address] = {
            #         'device_name': device_name,
            #         'rssi': rssi,
            #         'packet_data': packet_data
            #     }
            #     # print(device_name)
            #     worker.UI.emit(lambda: self.display_textBrowser.append(f'Address: {address}, Name: {device_name}, RSSI: {rssi}'))
            #     # datas = packet_data.get('connectable_advertisement_packet')
            #     datas = packet_data
            #     if datas != None:
            #         for key2, value2 in datas.items():
            #             worker.UI.emit(lambda: self.display_textBrowser.append(f'   {key2}'))
            #             for key3, value3 in value2.items():
            #                 worker.UI.emit(lambda: self.display_textBrowser.append(f'       {key3}: {value3}'))
            #     worker.UI.emit(lambda: self.display_textBrowser.append(f'\n'))
            
            # self.display_textBrowser.append('\n')



    def show_reply(self, data):
        print(__name__, data)
        self.display_textBrowser.append('handle: 0x{:2X}, value: {}'.format(data['data']['handle'], ['{:02X}'.format(i) for i in data['data']['value']]))
        
        
    def set_UI(self, function):
        function()
        self.logger.debug(function)

    def clear_textBrowser(self):
        self.display_textBrowser.setText('')

    def select_file(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "Open file", "./") # start path
        print(filename, filetype)
        self.textEdit_filePath.setText(filename)

    @do_in_thread
    def send_OTA_packet(self, cmd: eAmotaCommand, dataWillBeSent: bytearray) -> bool:
        packet = list()
        next_packet_start_idx = 0 # Point to the first byte of the next packet.
        data_buf = bytearray([])
        packet_serial_number = 0
        
        while next_packet_start_idx <= dataWillBeSent.__len__():
            packet_serial_number += 1

            ############ Check if the rest of the data can be downloaded at one time ############
            if dataWillBeSent.__len__() - next_packet_start_idx > OTA_PKT_DATA_MAX_LEN: 
                data_buf.clear()
                data_buf.extend(dataWillBeSent[next_packet_start_idx: next_packet_start_idx + OTA_PKT_DATA_MAX_LEN])
                next_packet_start_idx += OTA_PKT_DATA_MAX_LEN
            else:
                data_buf.clear()
                data_buf.extend(dataWillBeSent[next_packet_start_idx:])
                next_packet_start_idx += data_buf.__len__() + 1 
                
            ############################ generate and send packet ###############################
            packet.clear()
            packet.extend(cov.swap_endian(cov.i16_to_u8_list(data_buf.__len__() + 4)))                  # length*2u
            packet.append(cmd.value)                                                                    # header:OTA_cmd*1u
            packet.extend(data_buf)                                                                     # data:0~64u
            packet.extend(cov.swap_endian(cov.i32_to_u8_list(self.ble.get_checksum_crc32(data_buf))))   # checksum*4u
            if cmd == eAmotaCommand.AMOTA_CMD_FW_DATA:
                self.ble.write(uuid_ota_rx, packet)
                reply = []
                time.sleep(0.21)
            else:
                reply = self.ble.read(uuid_ota_rx, packet, 1)
            logger.info('Number %d packet, Send %d bytes data, rest of the data %d bytes.', 
                        packet_serial_number, 
                        data_buf.__len__(), 
                        dataWillBeSent.__len__() - next_packet_start_idx)

            ################## return (according to value in data of reply) ######################
            # reply: [{'source': <str>, 'data': {'handle': <number>, 'value': <list>}}]
            if reply.__len__() > 0:
                value_in_reply = reply[0]['data']['value'] # [length*2u, cmd*1u, status*1u, data:0~4u]
                if value_in_reply.__len__() > 3:
                    if value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_SUCCESS.value:
                        logger.info('Send packet success.')
                        time.sleep(0.01)
                    elif value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_CRC_ERROR.value:
                        logger.error('Send packet failed, status = AMOTA_STATUS_CRC_ERROR.')
                        return False
                    elif value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_INVALID_HEADER_INFO.value:
                        logger.error('Send packet failed, status = AMOTA_STATUS_INVALID_HEADER_INFO.')
                        return False
                    elif value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_INVALID_PKT_LENGTH.value:
                        logger.error('Send packet failed, status = AMOTA_STATUS_INVALID_PACKET_LENGTH.')
                        return False
                    elif value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_INSUFFICIENT_BUFFER.value:
                        logger.error('Send packet failed, status = AMOTA_STATUS_INSUFFICIENT_BUFFER.')
                        return False
                    elif value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_INSUFFICIENT_FLASH.value:
                        logger.error('Send packet failed, status = AMOTA_STATUS_INSUFFICIENT_FLASH.')
                        return False
                    elif value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_UNKNOWN_ERROR.value:
                        logger.error('Send packet failed, status = AMOTA_STATUS_UNKNOWN_ERROR.')
                        return False
                    elif value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_FLASH_WRITE_ERROR.value:
                        logger.error('Send packet failed, status = AMOTA_STATUS_FLASH_WRITE_ERROR.')
                        return False
                    elif value_in_reply[3] == eAmotaStatus.AMOTA_STATUS_MAX.value:
                        logger.error('Send packet failed, status = AMOTA_STATUS_MAX.')
                        return False
            else:
                logger.warning('No reply or reply out time.')
        
        return True

    @do_in_thread
    def send_FW_header(self) -> bool:
        fw_header_read = bytearray([0]*48) # hearder size 固定是 48 bytes
        fw_header_read = self.__openedFile.read(48)
        
        if fw_header_read.__len__() < 48: # bin file for update < 48 bytes
            logger.warning('Invalid packed firmware length.')
            return False
        
        self.__fileSize = ((fw_header_read[11] & 255) << 24) + ((fw_header_read[10] & 255) << 16) + ((fw_header_read[9] & 255) << 8) + (fw_header_read[8] & 255)
        logger.info('File size = ' + str(self.__fileSize) + '.')
        logger.debug(f'Fw header size = {fw_header_read.__len__()} bytes.')
        # print('Send fw header ' , fw_header_read, '.')

        if self.send_OTA_packet(eAmotaCommand.AMOTA_CMD_FW_HEADER, fw_header_read):
            logger.info('Send firmware header success.')
            return True
        
        return False
    
    @do_in_thread
    def send_FW_data(self) -> bool:
        fw_data_read = bytearray([])
        self.__openedFile.seek(48) # skip header
        fw_data_read = self.__openedFile.read(self.__fileSize)

        logger.debug('data size = %d bytes.', fw_data_read.__len__())
        if fw_data_read.__len__() < self.__fileSize: # data actually size < hearder recorded's
            return False

        if self.send_OTA_packet(eAmotaCommand.AMOTA_CMD_FW_DATA, fw_data_read):
            logger.info('Send firmware data complete.')
            return True
        
        return False
    
    @do_in_thread
    def send_verify_cmd(self) -> bool:
        logger.info('Send firmware verify cmd.')
        if self.send_OTA_packet(eAmotaCommand.AMOTA_CMD_FW_VERIFY, bytearray([])):
            return True
        
    @do_in_thread
    def send_reset_cmd(self) -> bool:
        logger.info('Send firmware reset cmd.')
        if self.send_OTA_packet(eAmotaCommand.AMOTA_CMD_FW_RESET, bytearray([])):
            return True

    @do_in_thread
    def start_OTA_update(self):
        try:
            self.__openedFile = open(self.textEdit_filePath.toPlainText(), 'rb')
            self.__fileSize = os.stat(self.textEdit_filePath.toPlainText()).st_size

            if (self.__fileSize == 0):
                logger.warning('Open file failed, file path: %s, file size = 0 byte', self.textEdit_filePath.toPlainText())
                self.__openedFile.close()
            elif (self.send_FW_header() == False):
                logger.error('Send FW header failed, file size = %d bytes.', self.__fileSize)
                self.__openedFile.close()
            else:
                if (self.send_FW_data() == False):
                    logger.error('Send FW data failed, file size = %d bytes.', self.__fileSize)
                    self.__openedFile.close()
                elif (self.send_verify_cmd() == False):
                    logger.error('Send verify cmd failed, file size = %d bytes.', self.__fileSize)
                    self.__openedFile.close()
                else:
                    self.send_reset_cmd()
                    logger.info('Exit start_OTA_update')
                    self.__openedFile.close()
        except Exception as e:
            logger.error('!!!!!!start_OTA_update() Error !!!!!!, \nopen file path: %s, \nfile size = %d bytes. \nException: %s', 
                         self.textEdit_filePath.toPlainText(), 
                         self.__fileSize, 
                         e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = cr1_ble_command()
    win.show()
    sys.exit(app.exec_())

