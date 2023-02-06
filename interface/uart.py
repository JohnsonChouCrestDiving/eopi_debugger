from pickle import LIST
from signal import raise_signal
import serial
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from collections import deque


class UART(QThread):
    rx_data = pyqtSignal(dict)

    __instance = None
    def __new__(cls, port:str, baud_rate:int):
        if cls.__instance == None:
            cls.__instance= super().__new__(cls)
        return cls.__instance
        
    def __init__(self, port:str, baud_rate:int=115200) -> None:
        super(UART, self).__init__()
        
        self.port = port
        self.baud_rate = baud_rate
        self.buffer_size = 5000
        self.buffer = deque([])
        self.conn = None
        self.rx_data.emit({'source': 'UART', 'data': 123})

    def set_port(self, port):
        if self.conn != None:
            self.close()
        self.port = port

    def is_open(self):
        if self.conn != None:
            return self.conn.is_open
        else:
            return False
    
    def open(self, port:str, baud_rate:int):
        self.conn = serial.Serial(port, baud_rate)

    def close(self):
        self.conn.close()
        self.conn = None
    
    def run(self):
        while True:
            if self.conn != None:
                try:
                    while self.conn.in_waiting:
                        self.rx_data.emit({'source': 'UART', 'data': self.readline()})
                except:
                    pass

            else:
                time.sleep(0.1)

    def readline(self):
        data_raw = self.conn.readline()
        data = data_raw.decode()
        return data

    def _writelines(self, buffer:LIST):
        for i in range(len(buffer)):
            buffer[i]+='\r\n'
            buffer[i] = buffer[i].encode()
            self.conn.writelines([buffer[i]])
            time.sleep(0.01)

    def send(self, cmd:str):
        self._writelines([cmd])
    
    def sendlines(self, cmds:LIST):
        self._writelines(cmds)

if __name__ == '__main__':
    COM_PORT = 'COM7'
    BAUD_RATES = 115200
    u = UART(COM_PORT, BAUD_RATES)