#standard library
import os
import sys
import logging
from logging.config import fileConfig
from datetime import datetime
import threading

#third party
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#module

def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS",
            os.path.abspath(".")
        ),
        relative
    )
    
if getattr(sys, 'frozen', None):
    log_file_path = resource_path('logging.conf')
else:
    log_file_path = os.path.join(os.getcwd(), 'log', 'logging.conf')
fileConfig(log_file_path)

def create_logger(name = 'rotatingFileLogger', level = logging.DEBUG):
    """
    
    Args:
        name: looger_name in logging.conf.
        level: logger display level.

        **********************
        logging.NOTSET         LOW
        logging.DEBUG           |
        logging.INFO            |
        logging.WARNING         |
        logging.ERROR           |
        logging.CRITICAL      HIGH
        **********************

    Returns:
        Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # set root logger to WARNING to prevent the other imported module flooding
    logging.getLogger().setLevel(logging.WARNING)
    return logger