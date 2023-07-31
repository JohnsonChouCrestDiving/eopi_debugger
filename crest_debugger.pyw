#standard library
import sys
import os
sys.path.append(os.getcwd())

#third party
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication

#module
from interface.interface_worker import  GenericWorker, do_in_thread
from UI_crest_debugger import Ui_MainWindow
import logging
logger = logging.getLogger('bluetooth')
logger.setLevel(0)

#sub-module

worker = GenericWorker()
do_in_thread = do_in_thread(worker)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        Eng_mode = 0
        factory_test_func_use = 1
        super(MainWindow, self).__init__()
        self.setupUi(self)
        from page.factory_full_test.main import factory_test_func
        self.full_test = factory_test_func()
        self.full_test_Layout.addWidget(self.full_test)
        self.guiwindowtitle = r'EOPI debugger V02.01.00'

        if Eng_mode:
            if factory_test_func_use:
                from page.factory_full_test.main import factory_test_func
                self.factory_test = factory_test_func()
                self.tabWidget.addTab(self.factory_test, 'factory_test_function')

        self.tabWidget.setCurrentIndex(0)
        self.setWindowTitle(self.guiwindowtitle)
        self.windoe_icon = QIcon(r'picture\EOPI_icon.jpg')
        self.setWindowIcon(self.windoe_icon)
        if __name__ == '__main__':
            worker.UI.connect(self.set_UI)
        

    def set_UI(self, function):
        # logger.debug(function)
        function()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
