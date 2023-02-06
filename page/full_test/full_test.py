#standard library
import sys
import os
import time
import base64
import copy
from collections import namedtuple
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from interface.uart import UART
from common.convert import Data_convertor as cov
from common.UI_object import Right_click_menu_generator, TextBrowser_msg_handler
from common.config import Config_creator
# from log.logger import loggers

#sub-module
if __name__ == '__main__':
    from UI_full_test import Ui_full_test
else:
    from .UI_full_test import Ui_full_test

COM_PORT = 'COM7'
BAUD_RATES = 115200

cov = cov()
# dongle = UART(COM_PORT, BAUD_RATES)
worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class full_test(QWidget, Ui_full_test):
    
    def __init__(self):
        super(full_test, self).__init__()
        self.setupUi(self)
        self.config = Config_creator('full_test')
        self.config_path = self.config.get_path()
        # self.logger = loggers()
        # self.logger.msg.connect(self.set_UI)
        ###################  button ###################
        self.press_up_pushButton.clicked.connect(lambda: self.press_button('UP'))
        self.press_down_pushButton.clicked.connect(lambda: self.press_button('DOWN'))
        self.press_ok_pushButton.clicked.connect(lambda: self.press_button('OK'))
        self.press_light_pushButton.clicked.connect(lambda: self.press_button('B_LIGHT'))
        self.press_back_pushButton.clicked.connect(lambda: self.press_button('BACK'))
    
    @do_in_thread
    def press_button(self, cmd:str):
        dongle.send(cmd)
        
    def set_UI(self, function):
        function()
        self.logger.debug(function)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = full_test()
    win.show()
    sys.exit(app.exec_())

