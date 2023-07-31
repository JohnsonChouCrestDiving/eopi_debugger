#standard library
import sys
import os
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
from page.factory_full_test.frontend import frontend
from page.factory_full_test.backend import backend
from page.factory_full_test.msg import *
import logging
logger = logging.getLogger('RotatingFileHandler')
worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class factory_test_func(QWidget):
    def __init__(self):
        super(factory_test_func, self).__init__()
        ## Init value ##
        self._is_connecting = False # flag for connecting, control Btn Behavior
        self._gui_msg_sn = 0 # GUI message serial number
        self.frontend = frontend()
        self.backend = backend()
        self.frontend.setupUi(self)
        self.frontend.init_UI_color()

        worker.message.connect(self._msg_router)
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
        logger.debug('scan btn clicked')
        try:
            self.frontend.set_scan_start()
            self.backend.do_scan()
            self.frontend.set_devicelist(self.backend.get_scan_data())
            self.frontend.set_scan_end()
        except Exception as e:
            self._handle_err(e)
    
    @do_in_thread
    def _connect_device(self):
        logger.debug('connect')
        try:
            MAC_addrs, addrs_type, device_name = self.frontend.get_select_dev_bt_inf()
            self.frontend.set_conn_start()
            self._is_connecting = self.backend.do_conn_dev(MAC_addrs, addrs_type, device_name)
        finally:
            self.frontend.set_conn_end(
                self._is_connecting,
                self.backend.get_fw_version(),
                self.backend.get_fw_build_time(),
                self.backend.get_battery_volt(),
                MAC_addrs
            )

    @do_in_thread
    def _disconnect_dev(self):
        logger.debug('disconnect')
        self.frontend.set_disconn_start()
        self._is_connecting = self.backend.do_disconn_dev()
        self.frontend.set_disconn_end(self._is_connecting)

    @do_in_thread
    def _handle_connect_Btn_event(self):
        logger.debug('connect/disconnect btn clicked')
        try:
            self._disconnect_dev() if self._is_connecting else self._connect_device()
        except Exception as e:
            self._handle_err(e)

    @do_in_thread
    def _handle_test_Btn_event(self):
        logger.debug('test btn clicked')
        try:
            is_finish = False
            data = {}
            is_all_pass = False
            if self._is_connecting == False: 
                raise noConnServer()
            self.frontend.set_test_start()
            is_finish = self.backend.do_test()
            if is_finish:
                data, is_all_pass = self.backend.get_test_data()
        except Exception as e:
            self._handle_err(e)
        finally:
            self.frontend.set_test_end(is_finish, data, is_all_pass)

    def _select_file(self):
        logger.debug('select file btn clicked')
        self.frontend.select_file()

    @do_in_thread
    def _handle_updateFw_Btn_event(self):
        logger.debug('update fw btn clicked')
        try:
            is_finish = False
            is_succ = False
            if self._is_connecting == False:
                raise noConnServer()      
            self.frontend.set_update_fw_start()
            is_finish, is_succ = self.backend.do_update_fw(self.frontend.get_fw_file_path())
        except Exception as e:
            self._handle_err(e)
        finally: # UI deinit
           self.frontend.set_update_fw_end(is_finish, is_succ)

    def _handle_COM_open_Btn_event(self):
        logger.debug('open COM btn clicked')
        try:
            self.frontend.set_open_com_start()
            port_num = self.frontend.get_com_port_num()
            self.backend.do_open_com_port(port_num)
        except IOError:
            logger.error('Cannot open COM' + port_num)
            worker.message.emit([NotifyType.GUI_LOG.value, 'COM PORT ERR'])
        except Exception as e:
            self._handle_err(e)
        finally:
            self.frontend.set_open_com_end()

    @do_in_thread
    def _handle_calPSensor_Btn_event(self):
        logger.debug('calibrate pressure sensor btn clicked')
        try:
            is_succ, before_p, after_p, offset = False, 0, 0, 0
            if not self._is_connecting:
                raise noConnServer()
            self.frontend.set_calPSensor_start()
            is_succ, before_p, after_p, offset = self.backend.do_cal_pSensor()
        except Exception as e:
            self._handle_err(e)
        finally: # UI deinit
            self.frontend.set_calPSensor_end(is_succ, before_p, after_p, offset)
    
    def _handle_err(self, err: Exception):
        err_type = type(err)
        if serverNoResponse == err_type:
            worker.message.emit([NotifyType.GUI_LOG.value, err.msg])
            self.frontend.set_Btn_disable(False)
        elif noConnServer == err_type:
            worker.message.emit([NotifyType.GUI_LOG.value, 'NO CONN'])
        elif conditionShort == err_type:
            worker.message.emit([NotifyType.GUI_LOG.value, err.msg])
        elif serverDisconn == err_type:
            self._is_connecting = False
            self.frontend.set_disconn_end(self._is_connecting)
        else:
            worker.message.emit([NotifyType.GUI_LOG.value, err])
        logger.error(err)

    @do_in_thread
    def _handle_find_watch_event(self):
        logger.debug('find watch btn clicked')
        try:
            if not self._is_connecting:
                raise noConnServer()
            self.backend.find_watch()
        except Exception as e:
            self._handle_err(e)
    
    @do_in_thread
    def _handle_export_file_event(self):
        logger.debug('log readout btn clicked')
        try:
            is_succ = False
            if not self._is_connecting:
                raise noConnServer()
            self.frontend.set_export_file_start()
            is_succ, is_already_read = self.backend.do_export_log()
        except Exception as e:
            self._handle_err(e)
        finally:
            self.frontend.set_export_file_end(is_succ, is_already_read)
    
    @do_in_thread
    def _handle_write_sn_event(self):
        logger.debug('write sn btn clicked')
        try:
            is_ok = False
            respond_sn = ''
            if not self._is_connecting:
                raise noConnServer()
            self.frontend.set_write_sn_start()
            is_ok, respond_sn = self.backend.do_write_sn(self.frontend.get_input_sn())
        except Exception as e:
            self._handle_err(e)
        finally:
            self.frontend.set_write_sn_end(is_ok, respond_sn)

    @do_in_thread
    def _update_batt_volt(self):
        self.backend.reflash_batt_volt()
        self.frontend.reflash_UI_voltage(self.backend.get_battery_volt())

    def _show_GUI_message(self, info: str):
        self._gui_msg_sn += 1
        now = datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M:%S")
        if info in log_disp_inf.keys():
            message = f'[{self._gui_msg_sn}]{time:<25}{info:<20}- {log_disp_inf[info]}'
        else:
            message = f'[{self._gui_msg_sn}]{time:<25}{info}'
        self.frontend.print_GUI_msg(message)

    def _show_message_box(self, info: list):
        level = msg_box_inf[info[0]][0].value
        title = f'{msg_box_inf[info[0]][0].name}: {info[0]}'
        message = f'{msg_box_inf[info[0]][1]}'+ (f'\n{info[1]}' if len(info) > 1 else '')
        self.frontend.display_msg_box(level, title, message)

    def _touch_off_action(self, info: str):
        if 'Device been disconnected' == info:
            raise serverDisconn()
        elif 'updateBattVolt' in info:
            self._update_batt_volt()
        elif 'otaProgressBar' in info:
            value = int(info.split('otaProgressBar')[1])
            self.frontend.set_ota_progress_bar(value)
        elif 'comPortStatus' in info:
            status = info.split('comPortStatus')[1]
            self.frontend.set_COM_port_LED_state(True if 'Normal' == status else False)

    def _msg_router(self, msg_inf: list):
        try:
            if NotifyType.GUI_LOG.value == msg_inf[0]:
                self._show_GUI_message(msg_inf[1])
            elif NotifyType.MSG_BOX.value == msg_inf[0]:
                self._show_message_box(msg_inf[1:])
            elif NotifyType.ACTION.value == msg_inf[0]:
                self._touch_off_action(msg_inf[1])
        except Exception as e:
            self._handle_err(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = factory_test_func()
    win.frontend.show()
    sys.exit(app.exec_())
