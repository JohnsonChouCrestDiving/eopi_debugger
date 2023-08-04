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
from page.factory_full_test.msg import NotifyType
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
    __instance = None
    def __new__(cls):
        if cls.__instance == None:
            cls.__instance= super().__new__(cls)
        return cls.__instance

    def __init__(self):
        super(frontend, self).__init__()

    def set_scan_start(self):
        self._show_wait_logo()
        self.set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_scanDevice.setText("WAIT  5  SEC"))

    def set_devicelist(self, devices: list):
        worker.UI.emit(lambda: self._remove_devices_in_listWidget())
        worker.UI.emit(lambda: self._add_devices_in_listWidget(devices))
    
    def set_scan_end(self):
        self._hide_wait_logo()
        self.set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_scanDevice.setText("SCAN  DEVICE"))

    def set_conn_start(self):
        self.set_Btn_disable(True)
        self._show_wait_logo()
        worker.message.emit([NotifyType.GUI_LOG.value, 'CONN START'])
        worker.UI.emit(lambda: self.Btn_connect.setText("CONNECTING ..."))
    
    def set_conn_end(self, is_conn: bool, fw_ver: str, fw_build_t: str, battVolt, dev_addr: str):
        self.set_Btn_disable(False)
        self._hide_wait_logo()
        if is_conn:
            worker.UI.emit(lambda: self.label_currDevAddr.setText(dev_addr))
            worker.UI.emit(lambda: self.label_currFwVer.setText(fw_ver))
            worker.UI.emit(lambda: self.label_currFwTime.setText(fw_build_t))
            worker.UI.emit(lambda: self.label_currentBattVolt.setText(str(battVolt)))
            worker.UI.emit(lambda: self.Btn_connect.setText("<< DISCONNECT"))
            worker.message.emit([NotifyType.GUI_LOG.value, 'CONN END'])
        else:
            worker.UI.emit(lambda: self.Btn_connect.setText( "CONNECT >>"))
            worker.message.emit([NotifyType.GUI_LOG.value, 'CONN FAIL'])

    def set_disconn_start(self):
        self.set_Btn_disable(True)
        self._show_wait_logo()

    def set_disconn_end(self, is_conn: bool):
        if not is_conn:
            worker.UI.emit(lambda: self.label_currDevAddr.setText('N/A'))
            worker.UI.emit(lambda: self.label_currFwVer.setText('N/A'))
            worker.UI.emit(lambda: self.label_currFwTime.setText('N/A'))
            worker.UI.emit(lambda: self.label_currentBattVolt.setText('N/A'))
            worker.UI.emit(lambda: self.Btn_connect.setText( "CONNECT >>"))
        self.set_Btn_disable(False)
        self._hide_wait_logo()

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
        self._show_wait_logo()
        self.set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_devTest.setText('TESTING ...'))

    def set_test_end(self, is_test_finish: bool, test_result: dict, is_all_pass: bool):
        self._hide_wait_logo()
        worker.message.emit([NotifyType.GUI_LOG.value, 'TEST END'])
        print('is test  finish:', is_test_finish)
        print('test result:', test_result)
        if is_test_finish and test_result != None:
            self._show_test_result(test_result)
            self._add_test_history(is_all_pass)
            msg = 'TEST PASS' if is_all_pass else 'TEST FAIL'
            extended_msg = ''
            for test_case, value in test_result.items(): extended_msg += f'{test_case}: {value}\n'
            worker.message.emit([NotifyType.MSG_BOX.value, msg, extended_msg])
        else:
            worker.message.emit([NotifyType.MSG_BOX.value, 'FAIL'])
        self.set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_devTest.setText("<<  COMPREHENSIVE TEST  >>"))

    def get_com_port_num(self) -> str:
        port_num = self.lineEdit_COMport.text()
        if port_num == '':
            raise conditionShort('PORT NEED')
        return port_num
    
    def set_open_com_start(self):
        self.lineEdit_COMport.setReadOnly(True)
    
    def set_open_com_end(self):
        self.lineEdit_COMport.setReadOnly(False)

    def set_calPSensor_start(self):
        self._show_wait_logo()
        self.set_Btn_disable(True)
        worker.UI.emit(lambda: self.Btn_Calibrate.setText('CALIBRATING ...'))

    def set_calPSensor_end(self, is_succ: bool, before_p, after_p, offset):
        self._hide_wait_logo()
        if (is_succ==False and before_p==0 and after_p==0 and offset==0):
            worker.message.emit([NotifyType.MSG_BOX.value, 'FAIL'])
            worker.message.emit([NotifyType.GUI_LOG.value, 'CALIBRATE FAIL'])
        else:
            self._show_cal_result(is_succ, before_p, after_p, offset)
        self.set_Btn_disable(False)
        worker.UI.emit(lambda: self.Btn_Calibrate.setText('Calibrate >>'))

    def _show_cal_result(self, is_succ: bool, before_p, after_p, offset):
        extended_message = f'Before Calibrate: {before_p}\nAfter Calibrate: {after_p}\nOffset: {offset}'
        if is_succ:
            worker.message.emit([NotifyType.MSG_BOX.value, 'CAL PRESSURE SUCC', extended_message])
            worker.message.emit([NotifyType.GUI_LOG.value, 'CALIBRATE PASS'])
        else:
            worker.message.emit([NotifyType.MSG_BOX.value, 'CAL PRESSURE FAIL', extended_message])
            worker.message.emit([NotifyType.GUI_LOG.value, 'CALIBRATE FAIL'])

    def _show_test_result(self, test_result: dict):
        msg = 'Test result: \n'
        for test_case, value in test_result.items():
            msg += f'{test_case}: {value}\n'
        worker.message.emit([NotifyType.GUI_LOG.value, msg])

    def _add_test_history(self, is_pass: bool):
        self.textBrowser_testHistory.append(
            datetime.now().strftime("%m-%d %H:%M") 
            + '  '
            + ('PASS' if is_pass else 'FAIL') 
            + '  '
            + self.label_currDevAddr.text()
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

    def print_GUI_msg(self, message: str):
        worker.UI.emit(lambda: self.textBrowser_guiMessage.append(message))

    def get_fw_file_path(self) -> str:
        path = self.textEdit_filePath.toPlainText()
        if path == '':
            raise conditionShort('NO FILE')
        return path

    def set_update_fw_start(self):
        self.set_Btn_disable(True)
        worker.message.emit([NotifyType.GUI_LOG.value, 'START UPDATE FW'])
        worker.UI.emit(lambda: self.Btn_updataFw.setText('UPDATING ...'))
        self._show_wait_logo()
    
    def set_update_fw_end(self, is_finsh: bool, is_succ: bool):
        self.set_Btn_disable(False)
        self.progressBar_FwUpdate.reset()
        worker.UI.emit(lambda: self.Btn_updataFw.setText('Update FW'))
        self._hide_wait_logo()
        if is_finsh and is_succ:
            worker.message.emit([NotifyType.MSG_BOX.value, 'FW UPDATE SUCC'])
        elif is_finsh and not is_succ:
            worker.message.emit([NotifyType.MSG_BOX.value, 'FW UPDATE FAIL'])
        elif not is_finsh:
            worker.message.emit([NotifyType.MSG_BOX.value, 'FAIL'])

    def set_export_file_start(self):
        self._show_wait_logo()
        self.set_Btn_disable(True)
        worker.message.emit([NotifyType.GUI_LOG.value, 'START LOG READOUT'])

    def set_export_file_end(self, is_succ: bool, is_already_readout: bool):
        self._hide_wait_logo()
        if is_already_readout:
            worker.message.emit([NotifyType.MSG_BOX.value, 'LOG ALREADY READOUT'])
        elif is_succ:
            worker.message.emit([NotifyType.MSG_BOX.value, 'LOGREADOUT SUCC'])
        else:
            worker.message.emit([NotifyType.MSG_BOX.value, 'FAIL'])
        self.set_Btn_disable(False)
        worker.message.emit([NotifyType.GUI_LOG.value, 'LOG READOUT END'])
    
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
        self._show_wait_logo()
        worker.message.emit([NotifyType.GUI_LOG.value, 'WRITE SN'])
    
    def set_write_sn_end(self, is_succ: bool, res_sn: str):
        self.set_Btn_disable(False)
        self._hide_wait_logo()
        if not is_succ:
            worker.message.emit([
                NotifyType.MSG_BOX.value, 'SN WRITE FAIL',
                f'Watch receive SN: {res_sn}'
            ])
        else:
            worker.message.emit([
                NotifyType.MSG_BOX.value, 'SN WRITE SUCC',
                f'Watch receive SN: {res_sn}'
            ])
        worker.message.emit([NotifyType.GUI_LOG.value, 'WRITE SN END'])

    def init_UI_color(self):
        self.tabWidget_action.tabBar().setTabTextColor(0, QColor(255, 0, 0))
        self.tabWidget_action.tabBar().setTabTextColor(1, QColor(0, 255, 0))
        self.tabWidget_action.tabBar().setTabTextColor(2, QColor(0, 0, 255))
        self.LED_comPortOk.set_color(1)
        self.gif = QMovie(r'.\picture\wait_640x360-3s-q3.gif')
        self.label_waitMovie.setMovie(self.gif)
        self.label_waitMovie.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif.start()
        self.label_waitMovie.hide()

    def reflash_UI_voltage(self, volt):
        worker.UI.emit(lambda: self.label_currentBattVolt.setText(str(volt)))

    def display_msg_box(self, level, title, message):
        mbox = QMessageBox()
        if 0 == level: # mbox_type.INFO.value
            worker.UI.emit(lambda: mbox.information(self, title, message))
        elif 1 == level: # mbox_type.QUESTION.value
            worker.UI.emit(lambda: mbox.question(self, title, message))
        elif 2 == level: # mbox_type.WARNING.value
            worker.UI.emit(lambda: mbox.warning(self, title, message))
        elif 3 == level: # mbox_type.CRITICAL.value
            worker.UI.emit(lambda: mbox.critical(self, title, message))

    def _show_wait_logo(self):
        worker.UI.emit(lambda: self.label_waitMovie.show())
    
    def _hide_wait_logo(self):
        worker.UI.emit(lambda: self.label_waitMovie.hide())

    def set_ota_progress_bar(self, progress):
        worker.UI.emit(lambda: self.progressBar_FwUpdate.setValue(progress))

    def set_COM_port_LED_state(self, is_normal: bool):
        worker.UI.emit(lambda: self.LED_comPortOk.set_color(2 if is_normal else 1))
