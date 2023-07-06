#standard library
import sys
import os
import time
from enum import Enum
import csv
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import openpyxl
from openpyxl.styles import PatternFill

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from interface.bluetooth.bluetooth import Bluetooth_LE, dongle
from common.convert import Data_convertor as cov
from common.UI_object import Right_click_menu_generator, TextBrowser_msg_handler
from common.config import Config_creator
import page.factory_test.CR1_bt as CR1
# from log.logger import loggers
import logging
logger = logging.getLogger('factory_test')

#sub-module
if __name__ == '__main__':
    from UI_factory_test_page import Ui_factory_test_func
else:
    from .UI_factory_test_page import Ui_factory_test_func

cov = cov()
worker = GenericWorker()
do_in_thread = do_in_thread(worker)

RSSI_LIMIT  = -60   # dBm, device will only display when the RSSI is higher than this value
SCAN_TIME   =   5   # seconds

class factory_test_func(QWidget, Ui_factory_test_func):
    def __init__(self):
        super(factory_test_func, self).__init__()
        self.setupUi(self)

        self.config = Config_creator('factory_test_func')
        self.config_path = self.config.get_path()
        # self._Qtranslate = QCoreApplication.translate
        self._ble = worker.ble
        self.dongle_used = dongle.bleuio.value
        if self._ble.client == None:
            self._ble.select_interface(self.dongle_used)
        self._display_devices = []
        self._is_testing = False
        self._is_connecting = False
        self._dev = CR1 # current test device module

        self.Btn_scanDevice.clicked.connect(self.handle_scan_Btn_event)
        self.Btn_connect.clicked.connect(self.handle_connect_Btn_event)
        self.Btn_devTest.clicked.connect(self.handle_test_Btn_event)
        self.Btn_selectFile.clicked.connect(self._select_file)
        self.Btn_updataFw.clicked.connect(self.handle_updateFw_Btn_event)

        if __name__ == '__main__':
            worker.UI.connect(self.set_UI)

    @do_in_thread
    def handle_scan_Btn_event(self):
        if self._is_testing:
            # self._show_message_box('IN TESTING')
            return

        self._disconnect_dev()
        self.Btn_scanDevice.setText("W A I T     7     S E C S")
        self._ble.scan(timeout=SCAN_TIME, scan_cb=self._store_scan_data)
        self._set_devices_list()
        self.Btn_scanDevice.setText("S C A N        D E V I C E")

    def _set_devices_list(self):
        self._remove_devices_in_listWidget()
        self._sort_devices_by_rssi()
        self._add_devices_in_listWidget()

    def _store_scan_data(self, msg: dict, a, b):
        self._display_devices = []
        for value in msg.values():
            device_name, address, rssi, packet_data = self._get_inf_from_dongle_data(value)
            if rssi > RSSI_LIMIT:
                self._display_devices.append(
                    bt_dev_display_info(address, device_name, rssi, packet_data)
                )

    def _sort_devices_by_rssi(self):
        """
        @brief: Sort the devices by rssi from high to low.
        @note: Algorithm: merge sort.
        """      
        def merge(left, right):
            result = []

            while len(left) and len(right):
                if (left[0].rssi < right[0].rssi):
                    result.append(left.pop(0))
                else:
                    result.append(right.pop(0))

            result = result+left if len(left) else result+right
            return result

        def mergeSort(array):
            if len(array) < 2:
                return array

            mid = len(array)//2
            leftArray = array[:mid]
            rightArray = array[mid:]

            return merge(mergeSort(leftArray),mergeSort(rightArray))
        
        self._display_devices = mergeSort(self._display_devices)
        self._display_devices.reverse()
    
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

    def _add_devices_in_listWidget(self):
        font = QFont()
        font.setFamily("Neue Haas Grotesk Text Pro Medi")
        font.setPointSize(16)
        
        for dev in self._display_devices:
            new_item = QListWidgetItem()
            new_item.setText(dev.widgetItemText)
            new_item.setFont(font)
            new_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.listWidget_deviceList.addItem(new_item)
    
    def set_UI(self, function):
        function()
        self.logger.debug(function)

    def _get_inf_from_dongle_data(self, value):
        """
        @return (name, address, rssi, packet_data)
        """
        rtn = ()
        if self.dongle_used == dongle.bleuio.value:
            rtn = (
                value['name'], value['address'], value['rssi'], value['pkt_dat']
            )
        elif self.dongle_used == dongle.blueGiga.value:
            rtn = (
                value.name, value.address, value.rssi, value.packet_data
            )
        return rtn
    
    @do_in_thread
    def _connect_device(self):
        item_select = self.listWidget_deviceList.item(self.listWidget_deviceList.currentRow())

        if item_select != None:
            self.Btn_connect.setText("C O N N E C T I N G  ...")
            MAC_addrs = item_select.text().split(' - ')[-1].split(']')[-1]
            if self.Btn_connect.text() == "C O N N E C T I N G  ...":
                self._ble.connect(MAC_addrs)
                time.sleep(2)
                self._is_connecting = self._ble.is_connect()
            if self._is_connecting:
                self.label_currDevAddr.setText(MAC_addrs)
                self.label_currDevAddr.setAlignment(
                    Qt.AlignmentFlag.AlignJustify | Qt.AlignmentFlag.AlignVCenter
                )
                self.Btn_connect.setText("<<  D I S C O N N E C T")
        else:
            # self._show_message_box('NO SELECT DEV')
            pass

    @do_in_thread
    def _disconnect_dev(self):
        self._ble.disconnect()
        time.sleep(0.5)
        self._is_connecting = self._ble.is_connect()
        if self._is_connecting == False:
            self.label_currDevAddr.setText('N/A')
            self.Btn_connect.setText("C O N N E C T  >>")

    @do_in_thread
    def handle_connect_Btn_event(self):
        if self._is_testing:
            # self._show_message_box('IN TESTING')
            return
        
        if self._is_connecting:
            self._disconnect_dev()
        else:
            self._connect_device()

    @do_in_thread
    def handle_test_Btn_event(self):
        if self._is_connecting == False:
            # self._show_message_box('NO CONN')
            return
        elif self.lineEdit_DevSN.text() == '':
            # self._show_message_box('NO SN')
            return
        else:
            self._is_testing = True
            self.lineEdit_DevSN.setReadOnly(self._is_testing) # Avoid changing the SN during the test to cause the wrong file name of the test result
            self.Btn_devTest.setText('T E S T I N G ...')
            self._file_name = self.lineEdit_DevSN.text()
            btTest = self._dev.test()
            self._subscribe_app_uuid()
            if btTest.start(): # if test is finished
                self._file_data = btTest.get_result_data()
                self._generate_csv_file()
                self._add_test_history()
                self._is_testing = False
                self.lineEdit_DevSN.setReadOnly(self._is_testing) # Unlock SN read-only restrictions
                self.Btn_devTest.setText('F I N I S H    T E S T')
                time.sleep(1.5)
                self.Btn_devTest.setText("<<  C O M P R E H E N S I V E      T E S T  >>")

    @do_in_thread
    def _subscribe_app_uuid(self):
        self._ble.subscribe(
            self._dev.GATT_CONFIG['app_rx'][0], 
            self._dev.GATT_CONFIG['app_rx'][1]
        )
        self._ble.subscribe(
            self._dev.GATT_CONFIG['app_tx'][0],
            self._dev.GATT_CONFIG['app_tx'][1]
        )
        self._ble.enable_all_notify()

    def _generate_csv_file(self):
        self._isAllPass = True
        with open(self._file_name + '.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Test case', 'Value/Error code', 'Note'])
            for test_case, value in self._file_data.items():
                writer.writerow([test_case, value[0], value[1]])
                if value[1] != 'Pass':
                    self._isAllPass = False
    
    def _generate_xslx_file(self):
        self._isAllPass = True
        wb = openpyxl.Workbook()
        s1 = wb[self._file_name]
        s1['A1'].value = 'Test case'
        s1['A2'].value = 'Value/Error code'
        s1['A3'].value = 'Note' 
        row = 0
        for test_case, value in self._file_data.items():
            row += 2
            s1.cell(row, 0).value = test_case
            s1.cell(row, 1).value = value[0]
            s1.cell(row, 2).value = value[1]
            if value[1] != 'Pass':
                self._isAllPass = False
                for column in range(3):
                    s1.cell(row, column).fill = PatternFill(
                        fill_type='solid', fgColor='FF0000'
                    )
        wb.save(self._file_name + '.xlsx')

    def _add_test_history(self):
        font = QFont()
        font.setFamily("Neue Haas Grotesk Text Pro Medi")
        font.setPointSize(16)
        new_item = QListWidgetItem()
        new_item.setText(' ' if self._isAllPass else '*' + self._file_name + '.csv')
        new_item.setFont(font)
        new_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.listWidget_testFile.insertItem(0, new_item)

    def _select_file(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "Open file", "./") # start path
        logger.info('Select file: ' + filename + '.' + filetype)
        self.textEdit_filePath.setText(filename)

    @do_in_thread
    def handle_updateFw_Btn_event(self):
        if self._is_connecting == False:
            # self._show_message_box('NO CONN')
            return
        self.Btn_updataFw.setText('U P D A T I N G ...')
        self._subscribe_ota_uuid()
        if self.Btn_updataFw.text() == 'U P D A T I N G ...':
            ota_update = self._dev.fw_update(self.textEdit_filePath.toPlainText())
            error_code =  ota_update.start()
        if error_code:
            # self._show_message_box(str(error_code))
            self._disconnect_dev()
            self.Btn_updataFw.setText('Finish Update')
            time.sleep(1.5)
            self.Btn_updataFw.setText('Update FW')
    
    @do_in_thread
    def _subscribe_ota_uuid(self):
        self._ble.subscribe(
            self._dev.GATT_CONFIG['ota_rx'][0], 
            self._dev.GATT_CONFIG['ota_rx'][1]
        )
        self._ble.subscribe(
            self._dev.GATT_CONFIG['ota_tx'][0],
            self._dev.GATT_CONFIG['ota_tx'][1]
        )
        self._ble.enable_all_notify()
    
    def _show_message_box(self, info: str):
        # Execute this function will found error: QObject::setParent: Cannot set parent, new parent is in a different thread
        class mbox_type(Enum):
            INFO = 0
            QUESTION = 1
            WARNING = 2
            CRITICAL = 3
        mbox_disp_inf = {
            'NO SELECT DEV': [
                mbox_type.WARNING,
                'WARNING:', 
                'Please select a device, before connect.'
            ],
            'NO SN': [
                mbox_type.WARNING,
                'WARNING: None SN',
                'Please enter the serial number of the device, before test begin.'
            ],
            'IN TESTING': [
                mbox_type.INFO,
                'Test hasn\'t finish:',
                'The device is being tested, please wait for the test to finish and try again'
            ],
            'NO CONN': [
                mbox_type.WARNING,
                'WARNING: None connection',
                'Please connect the device, and try again.'
            ],
            'FW UPDATE SUCC': [
                mbox_type.INFO,
                'FW update:',
                'FW update successfully.'
            ],
            'OPEN FILE ERR': [
                mbox_type.CRITICAL,
                'ERROR: Open file',
                'Open file failed.'
            ],
            'FW HEADER ERR': [
                mbox_type.CRITICAL,
                'Send FW failed',
                'Check firmware update file is effective.'
            ],
            'FW DATA ERR': [
                mbox_type.CRITICAL,
                'Send FW failed',
                'Incomplete file, check firmware update file is effective.'
            ],
            'VERIFY FW ERR': [
                mbox_type.CRITICAL,
                'Verify FW failed',
                'firmware file has been sent, but the verifiy failed, please send the update file again'
            ],
        }
        mbox = QMessageBox()

        if mbox_disp_inf[info][0] == mbox_type.INFO:
            mbox.information(
                self, 
                mbox_disp_inf[info][1], 
                mbox_disp_inf[info][2]
            )
        elif mbox_disp_inf[info][0] == mbox_type.QUESTION:
            mbox.question(
                self, 
                mbox_disp_inf[info][1], 
                mbox_disp_inf[info][2]
            )
        elif mbox_disp_inf[info][0] == mbox_type.WARNING:
            mbox.warning(
                self, 
                mbox_disp_inf[info][1], 
                mbox_disp_inf[info][2]
            )
        elif mbox_disp_inf[info][0] == mbox_type.CRITICAL:
            mbox.critical(
                self, 
                mbox_disp_inf[info][1], 
                mbox_disp_inf[info][2]
            )

class bt_dev_display_info(object):
    def __init__(self, ble_addr: str, device_name: str, rssi: int, packet_data):
        self.addr = ble_addr
        self.device_name = device_name
        self.rssi = rssi
        self.packet_data = packet_data
        self.widgetItemText = f'{device_name} - ({rssi}) - {ble_addr}'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = factory_test_func()
    win.show()
    sys.exit(app.exec_())
