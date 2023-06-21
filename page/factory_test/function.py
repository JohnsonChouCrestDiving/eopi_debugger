#standard library
import sys
import os
import time
from enum import Enum
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from interface.bluetooth.bluetooth import Bluetooth_LE, dongle
from common.convert import Data_convertor as cov
from common.UI_object import Right_click_menu_generator, TextBrowser_msg_handler
from common.config import Config_creator
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
        self._scan_rssi_filter = -60

        self.Btn_scanDevice.clicked.connect(self._scan_device)
        self.Btn_connect.clicked.connect(self._handle_connect_Btn_event)

        if __name__ == '__main__':
            worker.UI.connect(self.set_UI)

    @do_in_thread
    def scan_device(self):
        self._display_devices = []

        self._disconnect_dev()
        self.Btn_scanDevice.setText("W A I T     7     S E C S")
        self._ble.scan(timeout=5, scan_cb=self._store_scan_data)
        self._sort_devices_by_rssi()
        self._remove_devices_in_listWidget()
        self._add_devices_in_listWidget()
        self.Btn_scanDevice.setText("S C A N        D E V I C E")

    def _store_scan_data(self, msg: dict, a, b):
        for key, value in msg.items():
            device_name, address, rssi, packet_data = self._get_inf_from_dongle_data(value)
            if rssi > self._scan_rssi_filter:
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
    
    def _connect_device(self):
        current_item = self.listWidget_deviceList.item(self.listWidget_deviceList.currentRow())

        if current_item != None:
            # self._show_message_box('WAIT TO CONN')
            MAC_addrs = current_item.text().split(' - ')[-1].split(']')[-1]
            self._ble.connect(MAC_addrs)
            time.sleep(2)
            if self._ble.is_connect():
                self.label_currDevAddr.setText(MAC_addrs)
                self.label_currDevAddr.setAlignment(
                    Qt.AlignmentFlag.AlignJustify | Qt.AlignmentFlag.AlignVCenter
                )
                self.Btn_connect.setText("<<  D I S C O N N E C T")

    def _disconnect_dev(self):
        self._ble.disconnect()
        time.sleep(0.5)
        if self._ble.is_connect() == False:
            self.label_currDevAddr.setText('N/A')
            self.Btn_connect.setText("C O N N E C T  >>")

    @do_in_thread
    def handle_connect_Btn_event(self):
        if self._ble.is_connect():
            self._disconnect_dev()
        else:
            self._connect_device()


    def _show_message_box(self, info: str):
        # Execute this function will found error: QObject::setParent: Cannot set parent, new parent is in a different thread
        class mbox_type(Enum):
            INFO = 0
            QUESTION = 1
            WARNING = 2
            CRITICAL = 3
        mbox_disp_inf = {
            'WAIT TO CONN': [
                mbox_type.INFO,
                'NOTE:', 
                'The "connect" button will change to "disconnect" when successfully connected.'
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
