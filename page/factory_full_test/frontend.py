#standard library
import sys
import os
import time
from enum import Enum
import csv
import serial
import re
from datetime import datetime
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import openpyxl
from openpyxl.styles import PatternFill

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from interface.bluetooth.bluetooth import dongle
from common.convert import Data_convertor as cov
from common.config import Config_creator
from Script.Bluetooth.CR1_bt import test, device, fw_update
from Error.err_cls import *
from common.UI_object import Timer_generator
import logging
logger = logging.getLogger('factory_test')

#sub-module
if __name__ == '__main__':
    from UI_factory_test_page import Ui_factory_test_func
else:
    from .UI_factory_test_page import Ui_factory_test_func

worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class frontend(QWidget, Ui_factory_test_func):
    def __init__(self):
        super(frontend, self).__init__()
        self.setupUi(self)
        self._gui_msg_sn = 0

    def set_scan_start(self):
        self._set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_scanDevice.setText("WAIT  5  SEC"))

    def set_devicelist(self, devices: list):
        worker.UI.emit(lambda: self._remove_devices_in_listWidget())
        worker.UI.emit(lambda: self._add_devices_in_listWidget(devices))
    
    def set_scan_end(self):
        self._set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_scanDevice.setText("SCAN  DEVICE"))

    def set_conn_start(self):
        self._set_Btn_disable(True)
        self.show_GUI_message('CONN START')
        worker.UI.emit(lambda: self.Btn_connect.setText("CONNECTING ..."))
    
    def set_conn_end(self, is_conn: bool, fw_ver: str, fw_build_t: str, dev_addr: str):
        self._set_Btn_disable(False)
        if is_conn:
            worker.UI.emit(lambda: self.label_currDevAddr.setText(dev_addr))
            worker.UI.emit(lambda: self.label_currFwVer.setText(fw_ver))
            worker.UI.emit(lambda: self.label_currFwTime.setText(fw_build_t))
            worker.UI.emit(lambda: self.Btn_connect.setText("<< DISCONNECT"))
            self.show_GUI_message('CONN END')
        else:
            worker.UI.emit(lambda: self.Btn_connect.setText( "CONNECT >>"))
            self.show_GUI_message('CONN FAIL')

    def set_disconn_start(self):
        self._set_Btn_disable(True)

    def set_disconn_end(self, is_conn: bool):
        if not is_conn:
            worker.UI.emit(lambda: self.label_currDevAddr.setText('N/A'))
            worker.UI.emit(lambda: self.label_currFwVer.setText('N/A'))
            worker.UI.emit(lambda: self.label_currFwTime.setText('N/A'))
            worker.UI.emit(lambda: self.Btn_connect.setText( "CONNECT >>"))
        self._set_Btn_disable(False)

    def get_select_dev_MAC_addr(self) -> str:
        item_select = self.listWidget_deviceList.item(self.listWidget_deviceList.currentRow())
        if item_select == None:
            raise conditionShort('NO SELECT DEV')
        addrs = item_select.text().split(' - ')[-1].split(']')[-1]
        return addrs

    def set_test_start(self):
        self._set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_devTest.setText('TESTING ...'))

    def set_test_end(self, is_test_finish: bool, test_result: dict, is_all_pass: bool):
        if is_test_finish:
            self.show_GUI_message('TEST END')
            self._show_test_result(test_result)
            self._add_test_history(is_all_pass)
        self._set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_devTest.setText("<<  COMPREHENSIVE TEST  >>"))

    def get_com_port_num(self) -> str:
        port_num = self.lineEdit_COMport.text()
        if port_num == '':
            raise conditionShort('NO COM')
        return port_num
    
    def set_open_com_start(self):
        self.lineEdit_COMport.setReadOnly(True)
    
    def set_open_com_end(self):
        self.lineEdit_COMport.setReadOnly(False)

    def set_calPSensor_start(self):
        self._set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_Calibrate.setText('CALIBRATING ...'))

    def set_calPSensor_end(self):
        self._set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_Calibrate.setText(' Calibrate >>'))

    def _show_test_result(self, test_result: dict):
        msg = 'Test result: \n'
        for test_case, value in test_result.items():
            msg += f'{test_case}: {value}\n'
        self.show_GUI_message(msg)

    def _add_test_history(self, is_pass: bool):
        self.textBrowser_testHistory.append(
            datetime.now().strftime("%m-%d %H:%M") 
            + '  '
            + ('PASS' if is_pass else 'FAIL') 
            + '  '
            + self.label_currDevAddr.text()
            + '\n'
        )
    
    def _remove_devices_in_listWidget(self, how_many=0):
        """
        @brief: Remove removes the item from the top of the list.
        @param: how_many(int), if 0 means will remove all.
        """
        if how_many == 0:
            self.listWidget_deviceList.clear()
        else:
            for i in range(how_many):
                self.listWidget_deviceList.removeItemWidget(
                    self.listWidget_deviceList.takeItem(0)
                )

    def _add_devices_in_listWidget(self, devices: list):
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(16)
        
        for dev in devices:
            new_item = QListWidgetItem()
            new_item.setText(dev.widgetItemText)
            new_item.setFont(font)
            new_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.listWidget_deviceList.addItem(new_item)
    
    def _set_Btn_disable(self, is_disable: bool):
        worker.UI.emit(lambda: self.Btn_scanDevice.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_connect.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_devTest.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_updataFw.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_Calibrate.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_findWatch.setDisabled(is_disable))
    
    def show_GUI_message(self, info: str):
        self._gui_msg_sn += 1
        mbox_disp_inf = {
            'NO SELECT DEV': 'Please select a device, before connect.',
            'NO SN': 'Please enter the serial number of the device, before test begin.',
            'IN TESTING': 'The device is being tested, please wait for the test to finish and try again',
            'NO CONN': 'Please connect the device, and try again.',
            'START UPDATE FW': 'Start update firmware, please wait...',
            'FW UPDATE SUCC': 'FW update successfully.',
            'OPEN FILE ERR': 'Open file failed.',
            'FW HEADER ERR': 'Check firmware update file is effective.',
            'FW DATA ERR': 'Incomplete file, check firmware update file is effective.',
            'VERIFY FW ERR': 'firmware file has been sent, but the verifiy failed, please send the update file again',
            'COM PORT ERR': 'Cannot open COM port, please check the COM port is correct.',
            'COM PORT OK': 'COM port has been opened successly.',
            'TEST FAIL': 'Bluetooth device no response, please connect the device again.',
            'TEST1 FAIL': 'Bluetooth device no response, please connect the device again.',
            'TEST2 FAIL': 'Bluetooth device no response, please connect the device again.',
            'TEST3 FAIL': 'Bluetooth device no response, please connect the device again.',
            'TEST4 FAIL': 'Bluetooth device no response, please connect the device again.',
            'TEST5 FAIL': 'Bluetooth device no response, please connect the device again.',
            'SCAN START': 'Scanning for bleutooth devices, please wait...',
            'SCAN END': 'Scan finished.',
            'CONN START': 'Connecting to device, please wait...',
            'CONN END': 'Connect success.',
            'CONN FAIL': 'Connect failed, device may not trun on.',
            'CALIBRATE PASS': 'Calibrate barometric success.',
            'RECIVE FAIL': 'Bluetooth device no response',
            'Pressure Invalid': 'Instrument Pressure out of range',
            'TEST END': 'Test finished.',
            'DEV DISCONN': 'Bluetooth device disconnected.',
            'NO FILE': 'Please select a file, before update firmware.',
            'NO COM': 'Please open a COM port, and try again.',
            'UNKNOW ERR': 'Please turn off and remove the bluetooth receiver then plug it back in and turn on the GUI',
            'CALIBRATE FAIL': 'Calibrate barometric failed, device recive error.',
        }
        now = datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M:%S")
        if info in mbox_disp_inf.keys():
            message = f'[{self._gui_msg_sn}]{time:<25}{info:<20}- {mbox_disp_inf[info]}'
        else:
            message = f'[{self._gui_msg_sn}]{time:<25}{info}'
        worker.UI.emit(lambda: self.textBrowser_guiMessage.append(message))
