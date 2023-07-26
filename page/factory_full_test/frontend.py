#standard library
import sys
import os
import time
from datetime import datetime
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from Error.err_cls import *
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
        worker.message.connect(self.show_GUI_message)
        self._gui_msg_sn = 0

    def set_scan_start(self):
        self.set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_scanDevice.setText("WAIT  5  SEC"))

    def set_devicelist(self, devices: list):
        worker.UI.emit(lambda: self._remove_devices_in_listWidget())
        worker.UI.emit(lambda: self._add_devices_in_listWidget(devices))
    
    def set_scan_end(self):
        self.set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_scanDevice.setText("SCAN  DEVICE"))

    def set_conn_start(self):
        self.set_Btn_disable(True)
        self.show_GUI_message('CONN START')
        worker.UI.emit(lambda: self.Btn_connect.setText("CONNECTING ..."))
    
    def set_conn_end(self, is_conn: bool, fw_ver: str, fw_build_t: str, dev_addr: str):
        self.set_Btn_disable(False)
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
        self.set_Btn_disable(True)

    def set_disconn_end(self, is_conn: bool):
        if not is_conn:
            worker.UI.emit(lambda: self.label_currDevAddr.setText('N/A'))
            worker.UI.emit(lambda: self.label_currFwVer.setText('N/A'))
            worker.UI.emit(lambda: self.label_currFwTime.setText('N/A'))
            worker.UI.emit(lambda: self.Btn_connect.setText( "CONNECT >>"))
        self.set_Btn_disable(False)

    def get_select_dev_bt_inf(self):
        """
        @retrun: (MAC address(str), B.T. address type(str), device name(str))
        """
        item_select = self.listWidget_deviceList.item(self.listWidget_deviceList.currentRow())
        if item_select == None:
            raise conditionShort('NO SELECT DEV')
        name = item_select.text().split(' - ')[0]
        addr_inf = item_select.text().split(' - ')[-1].split(']')
        return addr_inf[-1], addr_inf[0], name

    def set_test_start(self):
        self.set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_devTest.setText('TESTING ...'))

    def set_test_end(self, is_test_finish: bool, test_result: dict, is_all_pass: bool):
        if is_test_finish:
            self.show_GUI_message('TEST END')
            self._show_test_result(test_result)
            self._add_test_history(is_all_pass)
        self.set_Btn_disable(False)
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
        self.set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_Calibrate.setText('CALIBRATING ...'))

    def set_calPSensor_end(self, volt: int):
        self.set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_Calibrate.setText('Calibrate >>'))
        worker.UI.emit(lambda: self.label_currDevVolt.setText(str(volt)))

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
    
    def set_Btn_disable(self, is_disable: bool):
        worker.UI.emit(lambda: self.Btn_scanDevice.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_connect.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_devTest.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_updataFw.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_Calibrate.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_findWatch.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_LogReadout.setDisabled(is_disable))
        worker.UI.emit(lambda: self.Btn_enterSN.setDisabled(is_disable))
    
    def show_GUI_message(self, info: str):
        if 'Device disconnect!' == info: # TODO
            self.set_disconn_end(False)

        self._gui_msg_sn += 1
        mbox_disp_inf = {
            'NO SELECT DEV': 'Please select a device, before connect.',
            'NO SN': 'Please enter the serial number of the device, and try again.',
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

    def get_fw_file_path(self) -> str:
        path = self.textEdit_filePath.toPlainText()
        if path == '':
            raise conditionShort('NO FILE')
        return path

    def set_update_fw_start(self):
        self.set_Btn_disable(True)
        self.show_GUI_message('START UPDATE FW')
        worker.UI.emit(lambda: self.Btn_updataFw.setText('UPDATING ...'))
    
    def set_update_fw_end(self):
        self.set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_updataFw.setText('Finish Update'))
        time.sleep(1.5)
        worker.UI.emit(lambda: self.Btn_updataFw.setText('Update FW'))

    def set_export_file_start(self):
        self.set_Btn_disable(True)
        self.show_GUI_message('START LOG READOUT')

    def set_export_file_end(self):
        self.set_Btn_disable(False)
        self.show_GUI_message('LOG READOUT END')
    
    def get_input_sn(self) -> str:
        sn = self.lineEdit_DevSN.text()
        if sn == '':
            raise conditionShort('NO SN')
        return sn

    def select_file(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "Open file", "./") # start path
        logger.info('Select file: ' + filename + '.' + filetype)
        worker.UI.emit(lambda: self.textEdit_filePath.setText(filename))

    def set_write_sn_start(self):
        self.set_Btn_disable(True)
        self.show_GUI_message('WRITE SN')
    
    def set_write_sn_end(self):
        self.set_Btn_disable(False)
        self.show_GUI_message('WRITE SN END')

    def _show_pass_logo(self):
        pass
    
    def _show_fail_logo(self):
        pass

    def _show_wait_logo(self):
        pass
