import sys, os
import asyncio
import time

from .bleak.bleak import BleakClient, BleakScanner, discover
import logging
from logging.config import fileConfig

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

logger = logging.getLogger()
logger.setLevel(0)
address4 = 'E8:E9:2E:EC:9E:8A'

loop = asyncio.get_event_loop()

def kill_loop():
    loop.close()

def create_loop():
    loop = asyncio.get_event_loop()

class ble_bleak():
    _instance = None
    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.client = None
        self.loop = loop

    def connect(self, addr):
        logger.debug(f'ble-bleak connect {addr}...')
        self.client = BleakClient(addr)
        self.loop.run_until_complete(self._connect_async(addr))


    def disconnect(self):
        logger.debug(f'ble-bleak disconnect...')
        self.loop.run_until_complete(self._disconnect_async())
        self.client = None

    def is_connect(self):
        try:
            return self.client.is_connected
        except:
            return False

    def get_service_uuid(self)->list:
        return [service.uuid for service in self.client.services]

    def send_command(self, uuid, datas:list):
        logger.debug(f'ble-bleak send command: uuid: {uuid}, command:{datas}')
        self.loop.run_until_complete(self._send_command_async(uuid, datas))

    def subscribe(self, uuid, callback, indication=True):
        logger.debug(f'ble-bleak enable notify: {uuid}, indication:{indication}')
        self.loop.run_until_complete(self._enable_indication_notification_async(uuid, callback, indication = indication))

    async def _connect_async(self, addr):
        try: 
            await self.client.connect(timeout=15)
            logger.debug(f'ble-bleak connect status: {self.client.is_connected}')
        except:
            logger.debug(f'ble-bleak connect ERROR !!!!!')

    async def _disconnect_async(self):
        # status = await self.client.disconnect()
        try:
            status = await self.client.disconnect()
            logger.debug(f'ble-bleak disconnect status: {status}')
        except:
            logger.debug(f'ble-bleak disconnect ERROR !!!!!')
        
        
        self.client = None

    async def _send_command_async(self, uuid, datas:list):
        try:
            status = await self.client.write_gatt_char(uuid, bytearray(datas))
            logger.debug(f'ble-bleak {uuid} send command status: {status}')
        except:
            logger.debug(f'ble-bleak {uuid} send command status: ERROR !!!!!')

    async def _enable_indication_notification_async(self, uuid, callback, indication=True):
        try:
            status = await self.client.start_notify(uuid, callback, force_indicate = indication)
            logger.debug(f'ble-bleak enable notify {uuid} status: {status}')
        except:
            logger.debug(f'ble-bleak enable notify {uuid} status: ERROR !!!!!')

if __name__ == '__main__':
    aa = ble_bleak()
    aa.connect(address4)
