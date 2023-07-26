#standard library
import sys
import os
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from Error.err_cls import *
from page.factory_full_test.frontend import frontend
from page.factory_full_test.backend import backend
import logging
logger = logging.getLogger('factory_test')
worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class factory_test_func(QWidget):
    def __init__(self):
        super(factory_test_func, self).__init__()
        ## Init value ##
        self._is_connecting = False # flag for connecting, control Btn Behavior
        self.frontend = frontend()
        self.backend = backend()
        self.frontend.setupUi(self)

        # self.LED_GuiNormal.set_color(2)
        self.frontend.Btn_scanDevice.clicked.connect(self._handle_scan_Btn_event)
        self.frontend.Btn_connect.clicked.connect(self._handle_connect_Btn_event)
        self.frontend.Btn_devTest.clicked.connect(self._handle_test_Btn_event)
        self.frontend.Btn_selectFile.clicked.connect(self._select_file)
        self.frontend.Btn_updataFw.clicked.connect(self._handle_updateFw_Btn_event)
        self.frontend.Btn_COMportOpen.clicked.connect(self._handle_COM_open_Btn_event)
        self.frontend.Btn_Calibrate.clicked.connect(self._handle_calPSensor_Btn_event)
        self.frontend.Btn_findWatch.clicked.connect(self._handle_find_watch_event)
        self.frontend.Btn_LogReadout.clicked.connect(self._handle_export_file_event)
        self.frontend.Btn_enterSN.clicked.connect(self._handle_write_sn_event)

    @do_in_thread
    def _handle_scan_Btn_event(self):
        try:
            self.frontend.set_scan_start()
            self.backend.do_scan()
            self.frontend.set_devicelist(self.backend.get_scan_data())
            self.frontend.set_scan_end()
        except Exception as e:
            self._handle_err(e)
    
    @do_in_thread
    def _connect_device(self):
        try:
            MAC_addrs, addrs_type, device_name = self.frontend.get_select_dev_bt_inf()
            self.frontend.set_conn_start()
            self._is_connecting = self.backend.do_conn_dev(MAC_addrs, addrs_type, device_name)
        finally:
            self.frontend.set_conn_end(
                self._is_connecting,
                self.backend.get_fw_version(),
                self.backend.get_fw_build_time(),
                MAC_addrs
            )

    @do_in_thread
    def _disconnect_dev(self):
        self.frontend.set_disconn_start()
        self._is_connecting = self.backend.do_disconn_dev()
        self.frontend.set_disconn_end(self._is_connecting)

    @do_in_thread
    def _handle_connect_Btn_event(self):
        try:
            self._disconnect_dev() if self._is_connecting else self._connect_device()
        except Exception as e:
            self._handle_err(e)

    @do_in_thread
    def _handle_test_Btn_event(self):
        try:
            is_finish = False
            if self._is_connecting == False: 
                raise serverNoConnect()
            self.frontend.set_test_start()
            is_finish = self.backend.do_test()
        except Exception as e:
            self._handle_err(e)
        finally:
            data, is_all_pass = self.backend.get_test_data()
            self.frontend.set_test_end(is_finish, data, is_all_pass)

    def _select_file(self):
        self.frontend.select_file()

    @do_in_thread
    def _handle_updateFw_Btn_event(self):
        try:
            if self._is_connecting == False:
                raise serverNoConnect()      
            self.frontend.set_update_fw_start()
            self.backend.do_update_fw(self.frontend.get_fw_file_path())
        except Exception as e:
            self._handle_err(e)
        finally: # UI deinit
           self.frontend.set_update_fw_end()

    def _handle_COM_open_Btn_event(self):
        try:
            self.frontend.set_open_com_start()
            port_num = self.frontend.get_com_port_num()
            self.backend.do_open_com_port(port_num)
        except IOError:
            logger.error('Cannot open COM' + port_num)
            self.frontend.show_GUI_message('COM PORT ERR')
        except Exception as e:
            self._handle_err(e)
        finally:
            self.frontend.set_open_com_end()

    @do_in_thread
    def _handle_calPSensor_Btn_event(self):
        try:
            if not self._is_connecting:
                raise serverNoConnect()
            self.frontend.set_calPSensor_start()
            self.backend.do_cal_pSensor()
        except Exception as e:
            self._handle_err(e)
        finally: # UI deinit
            self.frontend.set_calPSensor_end(self.backend.get_current_voltage())
    
    def _handle_err(self, err: Exception):
        err_type = type(err)
        if serverNoResponse == err_type:
            self.frontend.show_GUI_message(err.msg)
            # self._disconnect_dev()
            self.frontend.set_Btn_disable(False)
        elif serverNoConnect == err_type:
            self.frontend.show_GUI_message('NO CONN')
        elif conditionShort == err_type:
            self.frontend.show_GUI_message(err.msg)
        else:
            # self.LED_GuiNormal.set_color(1)
            logger.error(err)
            self.frontend.show_GUI_message('UNKNOW ERR')

    @do_in_thread
    def _handle_find_watch_event(self):
        try:
            if not self._is_connecting:
                raise serverNoConnect()
            self.backend.find_watch()
        except Exception as e:
            self._handle_err(e)
    
    @do_in_thread
    def _handle_export_file_event(self):
        try:
            if not self._is_connecting:
                raise serverNoConnect()
            self.frontend.set_export_file_start()
            self.backend.do_export_log()
        except Exception as e:
            self._handle_err(e)
        finally:
            self.frontend.set_export_file_end()
    
    def _handle_write_sn_event(self):
        try:
            self.frontend.set_write_sn_start()
            self.backend.do_write_sn(self.frontend.get_input_sn())
        except Exception as e:
            self._handle_err(e)
        finally:
            self.frontend.set_write_sn_end()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = factory_test_func()
    win.frontend.show()
    sys.exit(app.exec_())
