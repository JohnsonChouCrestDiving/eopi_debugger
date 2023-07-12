# (C) 2021 Smart Sensor Devices AB

import threading
import time

import serial.tools.list_ports

DONGLE_ARRAY = []


class BleuIo(object):
    def __init__(self, port="auto", baud=57600, timeout=1, debug=False):
        """
        Initiates the dongle. If port param is left as 'auto' it will auto-detect if bleuio dongle is connected.
        :param port: str
        :param baud: int
        :param timeout: int
        :param debug: bool
        """
        self.block_time = timeout
        retry_count = 0
        self._serial = None
        self._port = None
        self._debug = debug

        if port == "auto":
            dongle_count = 1
            port_list = []
            while len(DONGLE_ARRAY) == 0 and retry_count < 10:
                all_ports = serial.tools.list_ports.comports(include_links=False)
                for d_port in all_ports:
                    if str(d_port.hwid).__contains__("VID:PID=2DCF"):
                        bleuio_dongle = (
                            str(dongle_count) + ") " + d_port.device + " " + d_port.hwid
                        )
                        if bleuio_dongle.__contains__("VID:PID=2DCF:6002"):
                            if self._debug:
                                print("Found dongle in port: " + d_port.device)
                            DONGLE_ARRAY.append(bleuio_dongle)
                            port_list.append(d_port)
                            dongle_count += 1
                        if bleuio_dongle.__contains__("VID:PID=2DCF:6001"):
                            if self._debug:
                                print("Bootloader in port: " + d_port.device)
                            time.sleep(2)
                            retry_count = 0
                    else:
                        pass
                retry_count += 1
            time.sleep(2)

            try:
                self._serial = serial.Serial(
                    port=port_list[0].device, baudrate=baud, timeout=timeout
                )
                self._port = port_list[0].device
            except (serial.SerialException, IndexError):
                raise

        else:
            if not isinstance(port, str):
                raise ValueError("Invalid port specified: {}".format(port))
            while self._serial is None:
                try:
                    self._serial = serial.Serial(
                        port=port, baudrate=baud, timeout=timeout, write_timeout=timeout
                    )
                    self._port = port
                except (ValueError, serial.SerialException) as e:
                    retry_count += 1
                    if retry_count > 3:
                        print("Error: " + str(e))
                        print("Make sure the dongle is not already in use.")
                        exit()
                    else:
                        if self._debug:
                            print(
                                "Error occurred while trying to open port. "
                                + str(e)
                                + " Retrying %d/%d...",
                                retry_count,
                                3,
                            )
                        time.sleep(1)

            self._serial.flushInput()
            self._serial.flushOutput()

        self._continue = True
        self._thread_rx = threading.Thread(
            target=self.__task_rx, args=(), name="bleuio-rx@" + self._port
        )
        self._thread_tx = threading.Thread(
            target=self.__task_tx, args=(), name="bleuio-tx@" + self._port
        )
        self._thread_tx.setDaemon(True)
        self._thread_rx.setDaemon(True)
        self.__threadLock = threading.Lock()

        # rx task state
        self.rx_buffer = b""
        self.rx_response = []
        self.rx_scanning_results = []
        self.rx_sps_results = []
        self.__set_rx_state("rx_ready")
        self._scanning = False
        self._spsstream = False
        # self._show_sps_response = False

        # tx task state
        self.__set_tx_state("tx_waiting")
        self.cmd = ""

    def __task_rx(self):
        self.rx_buffer = b""
        while self._continue:
            self.__poll_serial()

    def __task_tx(self):
        while self._continue:
            if self.__get_tx_state() == "tx_ready":
                # time.sleep(0.02)
                if not self.cmd == "":
                    self.__send_command(self.cmd)

    def __poll_serial(self):
        try:
            self.rx_buffer = self._serial.read(self._serial.in_waiting)
        except Exception:
            pass
        if not self.rx_buffer.isspace():
            if self.rx_buffer.__contains__(str.encode("\r\n")):
                if "\r\nSCANNING" in self.rx_buffer.decode("utf-8", "ignore"):
                    self._scanning = True
                if "\r\nSCAN COMPLETE" in self.rx_buffer.decode("utf-8", "ignore"):
                    self._scanning = False
                if self._debug:
                    print("FROM BUFFER: " + self.rx_buffer.decode("utf-8", "ignore"))
                if self._scanning:
                    if "Device" in self.rx_buffer.decode("utf-8", "ignore"):
                        self.rx_scanning_results.append(
                            self.rx_buffer.decode("utf-8", "ignore")
                        )
                if self._spsstream:
                    self.rx_sps_results.append(self.rx_buffer.decode("utf-8", "ignore"))
                if not self.__get_rx_state() == "rx_ready" and not self._scanning:
                    self.rx_response.append(self.rx_buffer.decode("utf-8", "ignore"))
                    time.sleep(0.02)
        self.rx_buffer = b""

    def start_daemon(self):
        """
        Initiates a thread which manages all traffic received from serial
        and dispatches it to the appropriate callback
        """
        self._continue = True
        self._thread_rx.start()
        self._thread_tx.start()

    def stop_daemon(self):
        """
        Stops the thread which is monitoring the serial port for incoming
        traffic from the devices.
        """
        self._continue = False
        self._thread_rx.join()
        self._thread_tx.join()
        self._serial.close()

    def send_command(self, cmd):
        """
        :param cmd: Data to be sent over serial.
        """
        self._serial.flush()
        self.cmd = cmd
        # self.__threadLock.acquire()
        self.__set_tx_state("tx_ready")
        # self.__threadLock.release()
        self.rx_buffer = b""

    def __set_tx_state(self, state):
        self.__threadLock.acquire()
        self.tx_state = state
        self.__threadLock.release()

    def __set_rx_state(self, state):
        self.__threadLock.acquire()
        self.rx_state = state
        self.__threadLock.release()

    def __get_tx_state(self):
        self.__threadLock.acquire()
        state = self.tx_state
        self.__threadLock.release()
        return state

    def __get_rx_state(self):
        self.__threadLock.acquire()
        state = self.rx_state
        self.__threadLock.release()
        return state

    def __send_command(self, cmd):
        self.rx_response = []
        self._serial.reset_output_buffer()
        if cmd.__eq__("stop"):
            self._serial.write("\x03".encode())
            self.__set_tx_state("tx_waiting")
            self.__set_rx_state("rx_waiting")
            self.cmd = ""
        elif cmd.__eq__("esc"):
            self._serial.write("\x1B".encode())
            self.__set_tx_state("tx_waiting")
            self.__set_rx_state("rx_waiting")
            self.cmd = ""
        else:
            if not cmd == "":
                self._serial.write(cmd.encode())
                self._serial.write(str.encode("\r"))
                # self.__threadLock.acquire()
                self.__set_tx_state("tx_waiting")
                self.__set_rx_state("rx_waiting")
                # self.__threadLock.release()
                self.cmd = ""

    def __at(self):
        response = ""
        self.send_command("AT")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nOK\r\n"]
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __ata(self, isOn):
        response = ""
        if isOn:
            self.send_command("ATA1")
        if not isOn:
            self.send_command("ATA0")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if (
                self.rx_response.__contains__("Show Ascii Off!\r\n")
                or "Show Ascii On!\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __atasps(self, isOn):
        response = ""
        if isOn:
            self.send_command("ATASPS1")
        if not isOn:
            self.send_command("ATASPS0")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if (
                self.rx_response.__contains__("Show SPS Ascii Off!\r\n")
                or "Show SPS Ascii On!\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __atds(self, isOn):
        response = ""
        if isOn:
            self.send_command("ATDS1")
        if not isOn:
            self.send_command("ATDS0")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if (
                self.rx_response.__contains__("Auto discover Services On!\r\n")
                or "Auto discover Services Off!\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __ate(self, isOn):
        response = ""
        if isOn:
            self.send_command("ATE1")
        if not isOn:
            self.send_command("ATE0")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_response.__contains__("\r\nECHO OFF\r\n") or "\r\nECHO ON\r\n":
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __ati(self):
        response = ""
        self.send_command("ATI")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if (
                self.rx_response.__contains__("\r\nAdvertising\r\n")
                or "\r\nNot Advertising\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __atr(self):
        response = ""
        self.send_command("ATR")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_advdata(self, advData):
        response = ""
        if not advData == "":
            self.send_command("AT+ADVDATA=" + advData)
        elif advData == "":
            self.send_command("AT+ADVDATA")
        while not self.__get_rx_state() == "rx_ready":
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nADVERTISING DATA:"
            ):
                self.__set_rx_state("rx_ready")
                break
                # response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                # response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                break

    def __at_advdatai(self, advData):
        response = ""
        self.send_command("AT+ADVDATAI=" + advData)
        while not self.__get_rx_state() == "rx_ready":
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\niBeacon created with uuid:"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_advstart(self, conn_type, intv_min, intv_max, timer):
        response = ""
        if not (conn_type == "" and intv_min == "" and intv_max == "" and timer == ""):
            self.send_command(
                "AT+ADVSTART="
                + conn_type
                + ";"
                + intv_min
                + ";"
                + intv_max
                + ";"
                + timer
                + ";"
            )
        else:
            self.send_command("AT+ADVSTART")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nADVERTISING...\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_advstop(self):
        response = ""
        self.send_command("AT+ADVSTOP")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nADVERTISING STOPPED.\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_advresp(self, respData):
        response = ""
        if respData == "":
            self.send_command("AT+ADVRESP")
        else:
            self.send_command("AT+ADVRESP=" + respData)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nRESPONSE DATA:"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_cancel_connect(self):
        response = ""
        self.send_command("AT+CANCELCONNECT")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_central(self):
        response = ""
        self.send_command("AT+CENTRAL")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_clearnoti(self, handle):
        response = ""
        self.send_command("AT+CLEARNOTI=" + handle)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("status=0\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR") or (
                self.rx_buffer.decode("utf-8", "ignore").__contains__("status=")
                and not self.rx_buffer.decode("utf-8", "ignore").__contains__(
                    "status=0\r\n"
                )
            ):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_clearindi(self, handle):
        response = ""
        self.send_command("AT+CLEARINDI=" + handle)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("status=0\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR") or (
                self.rx_buffer.decode("utf-8", "ignore").__contains__("status=")
                and not self.rx_buffer.decode("utf-8", "ignore").__contains__(
                    "status=0\r\n"
                )
            ):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_client(self):
        response = ""
        self.send_command("AT+CLIENT")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_devicename(self, name):
        response = ""
        if name == "":
            self.send_command("AT+DEVICENAME")
        else:
            self.send_command("AT+DEVICENAME=" + name)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_dis(self):
        response = ""
        self.send_command("AT+DIS")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\ndis_info_end\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_dual(self):
        response = ""
        self.send_command("AT+DUAL")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_enter_passkey(self, passkey):
        response = ""
        self.send_command("AT+ENTERPASSKEY=" + passkey)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_findscandata(self, scandata):
        response = ""
        self.rx_scanning_results = []
        self.send_command("AT+FINDSCANDATA=" + scandata)
        response = ["\r\nSCANNING\r\n"]
        while not self._scanning:
            time.sleep(0.1)
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                response = ["\r\nERROR"]
        return response

    def __at_frssi(self, rssi):
        response = ""
        self.send_command("AT+FRSSI=" + rssi)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gapaddrtype(self, addr_type):
        response = ""
        if addr_type == "":
            self.send_command("AT+GAPADDRTYPE")
        else:
            self.send_command("AT+GAPADDRTYPE=" + addr_type)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nADDR_TYPE="
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gapconnect(self, addr, intv_min, intv_max, slave_latency, sup_timeout):
        response = ""
        adv_params = False
        if intv_min:
            if intv_max:
                if slave_latency:
                    if sup_timeout:
                        adv_params = True
                        self.send_command(
                            "AT+GAPCONNECT="
                            + addr
                            + "="
                            + intv_min
                            + ":"
                            + intv_max
                            + ":"
                            + slave_latency
                            + ":"
                            + sup_timeout
                            + ":"
                        )
        if not adv_params:
            self.send_command("AT+GAPCONNECT=" + addr)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nCONNECTED.\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if (
                self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR")
                or "\r\nDISCONNECTED.\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gapdisconnect(self):
        response = ""
        self.send_command("AT+GAPDISCONNECT")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nDISCONNECTED.\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gapdisconnectall(self):
        response = ""
        self.send_command("AT+GAPDISCONNECTALL")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "All connections terminated."
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gapiocap(self, io_cap):
        response = ""
        if io_cap == "":
            self.send_command("AT+GAPIOCAP")
        else:
            self.send_command("AT+GAPIOCAP=" + io_cap)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nI/O CAP ="):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nERROR"
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nCannot change IO Capability while connected!\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gappair(self, bonded):
        response = ""
        if bonded:
            self.send_command("AT+GAPPAIR=BOND")
        else:
            self.send_command("AT+GAPPAIR")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if bonded:
                if (
                    self.rx_buffer.decode("utf-8", "ignore").__contains__(
                        "\r\nBONDING SUCCESS"
                    )
                    or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                        "\r\nBLE_EVT_GAP_NUMERIC_REQUEST"
                    )
                    or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                        "\r\nBLE_EVT_GAP_PASSKEY_REQUEST"
                    )
                ):
                    self.__set_rx_state("rx_ready")
                    response = self.rx_response
            else:
                if (
                    self.rx_buffer.decode("utf-8", "ignore").__contains__(
                        "\r\nPAIRING SUCCESS"
                    )
                    or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                        "\r\nBLE_EVT_GAP_NUMERIC_REQUEST"
                    )
                    or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                        "\r\nBLE_EVT_GAP_PASSKEY_REQUEST"
                    )
                ):
                    self.__set_rx_state("rx_ready")
                    response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gapscan(self, timeout):
        response = ""
        self.rx_scanning_results = []
        if not timeout == 0:
            self.send_command("AT+GAPSCAN=" + str(timeout))
            self._scanning = True
            while not self.__get_rx_state().__eq__("rx_ready"):
                if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                    "\r\nSCAN COMPLETE\r\n"
                ):
                    self.__set_rx_state("rx_ready")
                    self._scanning = False
                    response = self.rx_response
                if self.rx_buffer.decode("utf-8", "ignore").__eq__("\r\nERROR"):
                    self.__set_rx_state("rx_ready")
                    self._scanning = False
                    response = ["\r\nERROR"]
                if self.__get_rx_state().__eq__("rx_ready"):
                    return response
        if timeout == 0:
            self.send_command("AT+GAPSCAN")
            while not self.__get_rx_state().__eq__("rx_ready"):
                if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                    "\r\nSCANNING"
                ):
                    self.__set_rx_state("rx_ready")
                    self._scanning = True
                    response = self.rx_response
                if self.rx_buffer.decode("utf-8", "ignore").__eq__("\r\nERROR"):
                    self.__set_rx_state("rx_ready")
                    self._scanning = False
                    response = ["\r\nERROR"]
                if self.__get_rx_state().__eq__("rx_ready"):
                    return response

    def __at_gapunpair(self, addr):
        response = ""
        if addr == "":
            self.send_command("AT+GAPUNPAIR")
        else:
            self.send_command("AT+GAPUNPAIR=" + addr)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nUNPARIED.\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nERROR"
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nFAILED TO UNPAIR.\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gapstatus(self):
        response = ""
        self.send_command("AT+GAPSTATUS")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("Advertising"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gattcread(self, uuid):
        response = ""
        self.send_command("AT+GATTCREAD=" + uuid)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nSize:"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gattcwrite(self, uuid, data):
        response = ""
        self.send_command("AT+GATTCWRITE=" + uuid + " " + data)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nDATA WRITTEN:"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gattcwriteb(self, uuid, data):
        response = ""
        self.send_command("AT+GATTCWRITEB=" + uuid + " " + data)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nSize:"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gattcwritewr(self, uuid, data):
        response = ""
        self.send_command("AT+GATTCWRITEWR=" + uuid + " " + data)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nDATA WRITTEN:"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_gattcwritewrb(self, uuid, data):
        response = ""
        self.send_command("AT+GATTCWRITEWRB=" + uuid + " " + data)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nSize:"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_get_services(self):
        response = ""
        self.send_command("AT+GETSERVICES")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "handle_evt_gattc_browse_completed:"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_get_services_only(self):
        response = ""
        self.send_command("AT+GETSERVICESONLY")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nhandle_evt_gattc_discover_completed:"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_get_service_details(self, uuid):
        response = ""
        self.send_command("AT+GETSERVICEDETAILS=" + uuid)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nhandle_evt_gattc_browse_completed:"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_get_conn(self):
        response = ""
        self.send_command("AT+GETCONN")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "Our Role:"
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nNo Connections found.\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_indi(self):
        response = ""
        self.send_command("AT+INDI")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\n(conn_idx="
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nNo indications set!\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_noti(self):
        response = ""
        self.send_command("AT+NOTI")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\n(conn_idx="
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nNo notifications set!\r\n"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_numcompa(self, auto_accept):
        response = ""
        if auto_accept == "0":
            self.send_command("AT+NUMCOMPA=0")
        elif auto_accept == "1":
            self.send_command("AT+NUMCOMPA=1")
        elif auto_accept == "2":
            self.send_command("AT+NUMCOMPA")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if auto_accept == "2":
                if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                    self.__set_rx_state("rx_ready")
                    response = self.rx_response
            else:
                if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                    "\r\nNUMERIC COMPARISON AUTO-ACCEPT"
                ):
                    self.__set_rx_state("rx_ready")
                    response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_peripheral(self):
        response = ""
        self.send_command("AT+PERIPHERAL")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_scantarget(self, addr):
        response = ""
        self.send_command("AT+SCANTARGET=" + addr)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nSCANNING"):
                self.__set_rx_state("rx_ready")
                self._scanning = True
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__eq__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                self._scanning = False
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_sec_lvl(self, sec_lvl):
        response = ""
        if sec_lvl == "":
            self.send_command("AT+SECLVL")
        else:
            self.send_command("AT+SECLVL=" + sec_lvl)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "SECURITY LEVEL ="
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("ERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_server(self):
        response = ""
        self.send_command("AT+SERVER")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nOK\r\n"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_set_dis(self, manuf, model_num, serial_num, hw_rev, fw_rev, sw_rev):
        response = ""
        self.send_command(
            "AT+SETDIS="
            + manuf
            + "="
            + model_num
            + "="
            + serial_num
            + "="
            + hw_rev
            + "="
            + fw_rev
            + "="
            + sw_rev
        )
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nDIS Service info is set!"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_set_noti(self, handle):
        response = ""
        self.send_command("AT+SETNOTI=" + handle)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nhandle_evt_gattc_write_completed: conn_idx="
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_set_indi(self, handle):
        response = ""
        self.send_command("AT+SETINDI=" + handle)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nhandle_evt_gattc_write_completed: conn_idx="
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_set_passkey(self, passkey):
        response = ""
        if passkey == "":
            self.send_command("AT+SETPASSKEY")
        else:
            self.send_command("AT+SETPASSKEY=" + passkey)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nPASSKEY:"):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_show_rssi(self, rssi):
        response = ""
        if rssi:
            self.send_command("AT+SHOWRSSI=1")
        else:
            self.send_command("AT+SHOWRSSI=0")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nOK\r\n"
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nTarget conn indx="
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __at_spssend(self, data=""):
        response = ""
        if data == "":
            self.send_command("AT+SPSSEND")
            self.rx_sps_results = []
            while not self.__get_rx_state().__eq__("rx_ready"):
                if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                    "\r\nStreaming... [To abort press ESC-key!]"
                ):
                    self._spsstream = True
                    self.__set_rx_state("rx_ready")
                    response = self.rx_response
                if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                    self._spsstream = False
                    self.__set_rx_state("rx_ready")
                    response = ["\r\nERROR"]
                if self.__get_rx_state().__eq__("rx_ready"):
                    return response
        if not data == "":
            self.send_command("AT+SPSSEND=" + data)
            while not self.__get_rx_state().__eq__("rx_ready"):
                if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\n[Sent]"):
                    self.__set_rx_state("rx_ready")
                    response = self.rx_response
                if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                    self.__set_rx_state("rx_ready")
                    response = ["\r\nERROR"]
                if self.__get_rx_state().__eq__("rx_ready"):
                    return response

    def __at_target_conn(self, conn_idx):
        response = ""
        if conn_idx == "":
            self.send_command("AT+TARGETCONN")
        else:
            self.send_command("AT+TARGETCONN=" + conn_idx)
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nOK\r\n"
            ) or self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nTarget conn indx="
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __help(self):
        response = ""
        self.send_command("--H")
        while not self.__get_rx_state().__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "[A] = Usable in All Roles"
            ):
                self.__set_rx_state("rx_ready")
                response = self.rx_response
            if self.rx_buffer.decode("utf-8", "ignore").__contains__("\r\nERROR"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR"]
            if self.__get_rx_state().__eq__("rx_ready"):
                return response

    def __stop_scan(self):
        response = ""
        self.send_command("stop")
        while self._scanning:
            time.sleep(0.1)
        self.__set_rx_state("rx_ready")
        response = ["\r\nSCAN COMPLETE\r\n"]
        return response

    def __stop_sps(self):
        response = ""
        self.send_command("esc")
        while not self.rx_state.__eq__("rx_ready"):
            if self.rx_buffer.decode("utf-8", "ignore").__contains__(
                "\r\nStopped streaming."
            ):
                self._spsstream = False
                self.__set_rx_state("rx_ready")
                response = ["\r\nStopped streaming.\r\n"]
            if self.rx_buffer.decode("utf-8", "ignore").__eq__("\r\nERROR\r\n"):
                self.__set_rx_state("rx_ready")
                response = ["\r\nERROR\r\n"]
            if self.rx_state.__eq__("rx_ready"):
                return response

    def stop_scan(self):
        """
        Stops any type of scan.
        :return: str list
        """
        self.__stop_scan()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        # self._serial.flush()
        return self.rx_response

    def stop_sps(self):
        """
        Stops SPS Stream-mode.
        :return: str list
        """
        self.__stop_sps()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at(self):
        """
        Basic AT-Command.
        :return:
        """
        self.__at()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def ata(self, isOn):
        """
        Shows/hides ascii values from notification/indication/read responses.
        :param isOn: (boolean) True=On, False=Off
        :return:
        """
        self.__ata(isOn)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def atasps(self, isOn):
        """
        Toggle between ascii (Off) and hex responses (On) received from SPS.
        :param isOn: (boolean) True=On, False=Off
        :return:
        """
        self.__atasps(isOn)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def atds(self, isOn):
        """
        Turns auto discovery of services when connecting on/off.
        :param isOn: (boolean) True=On, False=Off
        :return:
        """
        self.__atds(isOn)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def ate(self, isOn):
        """
        Turns Echo on/off.
        :param isOn: (boolean) True=On, False=Off
        :return:
        """
        self.__ate(isOn)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def ati(self):
        """
        Device information query.
        :return: str
        """
        self.__ati()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def atr(self):
        """
        Trigger platform reset.
        :return: str
        """
        self.__atr()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_advdata(self, advdata=""):
        """
        Sets or queries the advertising data.
        :param: if left empty it will query what advdata is set
        :param advdata: hex str format: xx:xx:xx:xx:xx.. (max 31 bytes)
        :return: string[]
        """
        self.__at_advdata(advdata)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_advdatai(self, advdata):
        """
        Sets advertising data in a way that lets it be used as an iBeacon.
        Format = (UUID)(MAJOR)(MINOR)(TX)
        Example: at_advdatai(5f2dd896-b886-4549-ae01-e41acd7a354a0203010400)
        :param: if left empty it will query what advdata is set
        :param advdata: hex str
        :return: string[]
        """
        self.__at_advdatai(advdata)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_advstart(self, conn_type="", intv_min="", intv_max="", timer=""):
        """
        Starts advertising with default settings if no params.
        With params: Starts advertising with <conn_type><intv_min><intv_max><timer>.
        :param: Starts advertising with default settings.
        :param conn_type: str
        :param intv_min: str
        :param intv_max: str
        :param timer: str
        :return: string[]
        """
        self.__at_advstart(conn_type, intv_min, intv_max, timer)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_advstop(self):
        """
        Stops advertising.
        """
        self.__at_advstop()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_advresp(self, respData=""):
        """
        Sets or queries scan response data. Data must be provided as hex string.
        :param: if left empty it will query what advdata is set
        :param respData: hex str format: xx:xx:xx:xx:xx.. (max 31 bytes)
        :return: string[]
        """
        self.__at_advresp(respData)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_cancel_connect(self):
        """
        While in Central Mode, cancels any ongoing connection attempts.
        :return: string[]
        """
        self.__at_cancel_connect()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_central(self):
        """
        Sets the device Bluetooth role to central role.
        :return: string[]
        """
        self.__at_central()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_clearnoti(self, handle):
        """
        Disables notification for selected characteristic.
        :return: string[]
        """
        self.__at_clearnoti(handle)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_clearindi(self, handle):
        """
        Disables indication for selected characteristic.
        :return: string[]
        """
        self.__at_clearindi(handle)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_client(self):
        """
        Only in dual role.
        Sets the device role towards the targeted connection to client.
        :return: string[]
        """
        self.__at_client()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_divicename(self, name=""):
        """
        Gets or sets the device name.
        :return: string[]
        """
        self.__at_devicename(name)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_dis(self):
        """
        Shows the DIS Service info and if the DIS info is locked in or can be changed.
        :return: string[]
        """
        self.__at_dis()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_dual(self):
        """
        Sets the device Bluetooth role to dual role.
        :return: string[]
        """
        self.__at_dual()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_enter_passkey(self, passkey):
        """
        When faced with this message: BLE_EVT_GAP_PASSKEY_REQUEST use the AT+ENTERPASSKEY command to enter
        the 6-digit passkey to continue the pairing request.
        :param passkey: str: six-digit number string "XXXXXX"
        :return: string[]
        """
        self.__at_enter_passkey(passkey)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_findscandata(self, scandata):
        """
        Scans for all advertising/response data which contains the search params.
        :param scandata: str
        :return: string[]
        """
        response = self.__at_findscandata(scandata)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        self._serial.flush()
        return response

    def at_frssi(self, rssi):
        """
        Filters scan results, showing only results with <max_rssi> value or lower.
        :param rssi: str
        :return: string[]
        """
        self.__at_frssi(rssi)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gapaddrtype(self, addr_type=""):
        """
        Change device Address Type or queries device Address Type.
        :param addr_type: str
        :return: string[]
        """
        self.__at_gapaddrtype(addr_type)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gapconnect(
        self,
        addr,
        timeout=0,
        intv_min="",
        intv_max="",
        slave_latency="",
        sup_timeout="",
    ):
        """
        Initiates a connection with a specific slave device. [<addr_type>]<address>=<intv_min>:<intv_max>:<slave_latency>:<sup_timeout>
        :param addr: hex str format: [X]XX:XX:XX:XX:XX:XX
        :param timeout: int
        :param intv_min: str
        :param intv_max: str
        :param slave_latency: str
        :param sup_timeout: str
        :return: string[]
        """
        if timeout == 0:
            while (
                self.__at_gapconnect(
                    addr, intv_min, intv_max, slave_latency, sup_timeout
                )
                is None
            ):  # == None:
                time.sleep(0.1)
        else:
            self.__at_gapconnect(addr, intv_min, intv_max, slave_latency, sup_timeout)
            time.sleep(1.5 + timeout)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gapdisconnect(self):
        """
        Disconnects from a peer Bluetooth device.
        :return: string[]
        """
        self.__at_gapdisconnect()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gapdisconnectall(self):
        """
        Disconnects from all peer Bluetooth devices.
        :return: string[]
        """
        self.__at_gapdisconnectall()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gapiocap(self, io_cap=""):
        """
        Sets or queries what input and output capabilities the device has. Parameter is number between 0 to 4.
        :param io_cap: str: number
        :return: string[]
        """
        self.__at_gapiocap(io_cap)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gappair(self, bonded=False):
        """
        Starts a pairing (bonded=False) or bonding procedure (bonded=True).
        :param bonded: boolean
        :return: string[]
        """
        self.__at_gappair(bonded)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gapscan(self, timeout=0):
        """
        Starts a Bluetooth device scan with or without timer set in seconds.
        :param: if left empty it will scan indefinitely
        :param timeout: int (time in seconds)
        :return: string[]
        """
        response = self.__at_gapscan(timeout)
        time.sleep(0.5 + timeout)
        if timeout == 0:
            response = self.rx_response
        self.__set_rx_state("rx_ready")
        return response

    def at_gapunpair(self, addr_to_unpair=""):
        """
        Unpair paired devices if no parameters else unpair specific device. This will also remove the device bond data
        from BLE storage.
        Usable both when device is connected and when not.
        :param addr_to_unpair: hex str format: [X]XX:XX:XX:XX:XX:XX
        :return: string[]
        """
        self.__at_gapunpair(addr_to_unpair)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gapstatus(self):
        """
        Reports the Bluetooth role.
        :return: string[]
        """
        self.__at_gapstatus()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gattcread(self, uuid):
        """
        Read attribute of remote GATT server.
        :param uuid: hex str format: XXXX
        :return: string[]
        """
        self.__at_gattcread(uuid)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gattcwrite(self, uuid, data):
        """
        Write attribute to remote GATT server in ASCII.
        :param uuid: hex str format: XXXX 
        :param data: str
        :return: string[]
        """
        self.__at_gattcwrite(uuid, data)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gattcwriteb(self, uuid, data):
        """
        Write attribute to remote GATT server in Hex.
        :param uuid: hex str format: XXXX
        :param data: hex str format: XXXXXXX..
        :return: string[]
        """
        self.__at_gattcwriteb(uuid, data)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gattcwritewr(self, uuid, data):
        """
        Write, without response, attribute to remote GATT server in ASCII.
        :param uuid: hex str format: XXXX
        :param data: str
        :return: string[]
        """
        self.__at_gattcwritewr(uuid, data)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_gattcwritewrb(self, uuid, data):
        """
        Write, without response, attribute to remote GATT server in Hex.
        :param uuid: hex str format: XXXX
        :param data: hex str format: XXXXXXX..
        :return: string[]
        """
        self.__at_gattcwritewrb(uuid, data)
        time.sleep(0.01)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_get_services(self):
        """
        Discovers all services of a peripheral and their descriptors and characteristics.
        :return: string[]
        """
        self.__at_get_services()
        time.sleep(3)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_get_servicesonly(self):
        """
        Discovers a peripherals services.
        :return: string[]
        """

        # while self.__at_get_services_only() is None:
        #     time.sleep(0.1)
        self.__at_get_services_only()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_get_service_details(self, uuid):
        """
        Discovers all characteristics and descriptors of a selected service.
        :param uuid: hex str format: XXXX
        :return: string[]
        """
        self.__at_get_service_details(uuid)
        self.__set_rx_state("rx_ready")
        time.sleep(0.5)
        return self.rx_response

    def at_get_conn(self):
        """
        Gets a list of currently connected devices along with their mac addresses and conn_idx.
        :return: string[]
        """
        self.__at_get_conn()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_indi(self):
        """
        Show list of set indication handles.
        :return: string[]
        """
        self.__at_indi()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_noti(self):
        """
        Show list of set notification handles.
        :return: string[]
        """
        self.__at_noti()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_numcompa(self, auto_accept="2"):
        """
        Used for accepting a numeric comparison authentication request (no params) or enabling/disabling auto-accepting
        numeric comparisons. auto_accept="0" = off, auto_accept="1" = on.
        :param auto_accept: str format: "0" or "1"
        :return: string[]
        """
        self.__at_numcompa(auto_accept)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_peripheral(self):
        """
        Sets the device Bluetooth role to peripheral.
        :return: string[]
        """
        self.__at_peripheral()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_scantarget(self, addr):
        """
        Scan a target device. Displaying it's advertising and response data as it updates.
        :param addr: hex str format: "xx:xx:xx:xx:xx:xx"
        :return: string[]
        """
        self.__at_scantarget(addr)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_sec_lvl(self, sec_lvl=""):
        """
        Sets or queries (no params) what minimum security level will be used when connected to other devices.
        :param sec_lvl:  str: string number between 0 and 4
        :return: string[]
        """
        self.__at_sec_lvl(sec_lvl)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_server(self):
        """
        Only in dual role.
        Sets the device role towards the targeted connection to server.
        :return: string[]
        """
        self.__at_server()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_setdis(self, manuf, model_num, serial_num, hw_rev, fw_rev, sw_rev):
        """
        Sets the DIS Service info.
        :param manuf: str
        :param model_num: str
        :param serial_num: str
        :param hw_rev: str
        :param fw_rev: str
        :param sw_rev: str
        :return: string[]
        """
        self.__at_set_dis(manuf, model_num, serial_num, hw_rev, fw_rev, sw_rev)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_set_noti(self, handle):
        """
        Enable notification for selected characteristic.
        :param handle: hex str format: "xxxx"
        :return: string[]
        """
        self.__at_set_noti(handle)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_set_indi(self, handle):
        """
        Enable indication for selected characteristic.
        :param handle: hex str format: "xxxx"
        :return: string[]
        """
        self.__at_set_indi(handle)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_set_passkey(self, passkey=""):
        """
        Setting or quering set passkey (no params) for passkey authentication.
        :param passkey: hex str format: "xxxxxx"
        :return: string[]
        """
        self.__at_set_passkey(passkey)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_show_rssi(self, show_rssi=True):
        """
        Shows/hides RSSI in AT+FINDSCANDATA and AT+SCANTARGET scans.
        :param show_rssi: bool
        :return: string[]
        """
        self.__at_show_rssi(show_rssi)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_spssend(self, data=""):
        """
        Send a message or data via the SPS profile.
        Without parameters it opens a stream for continiously sending data.
        The streaming functions of the at_spssend() is unstable. We are working on fixing it.
        :param: if left empty it will open Streaming mode
        :param data: str
        :return: string[]
        """
        # self.__set_rx_state("rx_ready")
        # self.__set_tx_state("tx_waiting")
        # time.sleep(0.05)
        # while not self.__get_tx_state().__eq__("tx_waiting"):
        #     time.sleep(0.02)
        # while self.__get_rx_state().__eq__("rx_waiting"):
        #     time.sleep(0.02)
        # return self.rx_response
        self.__at_spssend(data)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def at_target_conn(self, conn_idx=""):
        """
        Set or quering the connection index which is the targeted connection.
        :param conn_idx: hex str format: xxxx
        :return: string[]
        """
        self.__at_target_conn(conn_idx)
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response

    def help(self):
        """
        Shows all AT-Commands.
        :return: string[]
        """
        self.__help()
        time.sleep(0.5)
        self.__set_rx_state("rx_ready")
        return self.rx_response