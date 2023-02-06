
import PyQt5
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from datetime import datetime
class UI_collector():
    def __init__(self):
        # self.UI_object = {
        #     'FW_Loader':{
        #         'LED':{}
        #     }
        # }
        self.LED = {}

    def collect_LED(self, page):
        for item in dir(page):
            if 'set_ok' in dir(getattr(page, item)):
                print(item)

class Right_click_menu_generator():
    def __init__(self, page:object, menus:dict):
        for item, action in menus.items():
            exec(f'self.{item}.setContextMenuPolicy(Qt.CustomContextMenu)', {'self':page, 'Qt':Qt})
            exec(f'self.{item}.customContextMenuRequested.connect(lambda sig: here.on_context_menu(sig, \'{item}\'))', {'self':page, 'here': self})
            exec(f'self.{item}_popMenu = QMenu(self)', {'self':page, 'QMenu': QMenu})
            
            for act, (func, args) in action.items():
                exec(f'self.{item}_popMenu_{act}_action = self.{item}_popMenu.addAction(\"{act}\")', {'self':page})
                connect_func = menus[item][act][func]
                connect_args = menus[item][act][args]
                exec(f'self.{item}_popMenu_{act}_action.triggered.connect(lambda sig: connect_func(**connect_args))', {'self':page, 'connect_func':connect_func, 'connect_args':connect_args})

        self.page = page
    def on_context_menu(self, point, item):
        # show context menu
        exec(f'self.{item}_popMenu.exec_(self.{item}.mapToGlobal({point}))', {'self':self.page, 'PyQt5':PyQt5})

    

class TextBrowser_msg_handler():
    def __init__(self, textBrowser):
        self.textBrowser = textBrowser

    def add_text(self, text):
        self.textBrowser.append(text)

    def add_text_top(self, text):
        self.textBrowser.textCursor().setPosition(0, 0)
        self.add_text(text)

    def add_error_text(self, msg):
        text = '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        text += '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        text += msg
        text += '\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        text += '\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        self.add_text(text)

    def add_error_text_top(self, text):
        self.textBrowser.textCursor().setPosition(0, 0)
        self.add_error_text(text)

    def clear_text(self):
        self.textBrowser.setText('')

    def add_text_with_time(self, text):
        now = datetime.now()
        t = now.strftime("%Y/%m/%d_%H:%M:%S\n")
        text = t+' '+text
        self.add_text(text)

    def add_error_text_with_time(self, text):
        now = datetime.now()
        t = now.strftime("%Y/%m/%d_%H:%M:%S\n")
        text = t+' '+text
        self.add_error_text(text)

    def show_the_top(self):
        self.textBrowser.verticalScrollBar().setValue(0)


class Timer_generator():
    def __init__(self, page:object, timers:dict):
        for item in timers.keys():
            timer = QTimer()
            timer.setInterval(timers[item]['interval'])
            for func in timers[item]['functions']:
                timer.timeout.connect(func)
            timers[item]['timer'] = timer
        
        self.timers = timers
        self.page = page


    def set_interval(self, name:str, interval:int):
        self.timers[name]['timer'].setInterval(interval)
        self.timers[name]['interval'] = interval


    def get_interval(self, name:str):
        return self.timers[name]['interval']

