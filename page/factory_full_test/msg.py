from enum import Enum
from PyQt5.QtWidgets import *

class mbox_type(Enum):
    INFO        = 0 
    QUESTION    = 1
    WARNING     = 2
    CRITICAL    = 3

log_disp_inf = {
    "NO SELECT DEV": "Please select a device, before connect.",
    "NO SN": "Please enter the serial number of the device, and try again.",
    "IN TESTING": "The device is being tested, please wait for the test to finish and try again",
    "NO CONN": "Please connect the device, and try again.",
    "START UPDATE FW": "Start update firmware, please wait...",
    "FW UPDATE SUCC": "FW update successfully.",
    "OPEN FILE ERR": "Open file failed.",
    "FW HEADER ERR": "Check firmware update file is effective.",
    "FW DATA ERR": "Incomplete file, check firmware update file is effective.",
    "VERIFY FW ERR": "firmware file has been sent, but the verifiy failed, please send the update file again",
    "COM PORT ERR": "Cannot open COM port, please check the COM port is correct.",
    "COM PORT OK": "COM port has been opened successly.",
    "TEST1 FAIL": "Bluetooth device no response, please connect the device again.",
    "TEST2 FAIL": "Bluetooth device no response, please connect the device again.",
    "TEST3 FAIL": "Bluetooth device no response, please connect the device again.",
    "TEST4 FAIL": "Bluetooth device no response, please connect the device again.",
    "TEST5 FAIL": "Bluetooth device no response, please connect the device again.",
    "SCAN START": "Scanning for bleutooth devices, please wait...",
    "SCAN END": "Scan finished.",
    "CONN START": "Connecting to device, please wait...",
    "CONN END": "Connect success.",
    "CONN FAIL": "Connect failed, device may not trun on.",
    "CALIBRATE PASS": "Calibrate barometric success.",
    "RECIVE FAIL": "Bluetooth device no response",
    "Pressure Invalid": "Instrument Pressure out of range",
    "TEST END": "Test finished.",
    "DEV DISCONN": "Bluetooth device disconnected.",
    "NO FILE": "Please select a file, before update firmware",
    "NO COM": "Please open a COM port, and try again.",
    "CALIBRATE FAIL": "Calibrate barometric failed, device reply error.",
    "SN WRITE OK": "Write Serial Number SUCCESSFULLY.",
    "PORT NEED": "Please input a COM port, and try again.",
}

msg_box_inf = {
    # title: [mbox_type, message]
    'FAIL': [mbox_type.CRITICAL, 'Action not finish, an unexpected problem occurred.'],
    'FW UPDATE SUCC': [mbox_type.INFO, 'Firmware update successfully.'],
    'FW UPDATE FAIL': [mbox_type.WARNING, 'OTA update firmware failed.'],
    'CAL PRESSURE SUCC': [mbox_type.INFO, 'Calibrate pressure success.'],
    'CAL PRESSURE FAIL': [mbox_type.WARNING, 'Can\'t calibrate watch\'s pressure value.'],
    'TEST PASS': [mbox_type.INFO, 'Test finish and all PASS.'],
    'TEST FAIL': [mbox_type.WARNING, 'Test finish and not all PASS.'],
    'SN WRITE SUCC': [mbox_type.INFO, 'Write Serial Number successfully.'],
    'SN WRITE FAIL': [mbox_type.WARNING, 'An unexpected problem occurred during Write SN.'],
    'LOGREADOUT SUCC': [mbox_type.INFO, 'Log readout successfully.'],
    'LOG ALREADY READOUT': [mbox_type.WARNING, 'Log has already been readout.'],
}

class NotifyType(Enum):
    GUI_LOG = 0
    MSG_BOX = 1
    ACTION  = 2
