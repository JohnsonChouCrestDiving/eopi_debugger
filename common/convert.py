#standard library
import struct
import base64
from math import log
#third party
#module
#sub-module


class Data_convertor():
    def __init__(self):
        pass

    def uint16_to_intList(self, data_list):
        intList = []
        for i in range(0, len(data_list), 2):
            intList.append(self.uint16_to_int(data_list[i:i+2]))
        return intList
    
    def uint16_to_int(self, data_list):
        return data_list[0]*256 + data_list[1]

    def int16_to_intList(self, data_list):
        intList = []
        for i in range(0, len(data_list), 2):
            intList.append(self.int16_to_int(data_list[i:i+2]))
        return intList
    
    def int16_to_int(self, data_list):
        if data_list[0] > 0x7f:
            data_list[0] = data_list[0] - 256
        return data_list[0]*256 + data_list[1]

    def uint32_to_intList(self, data_list):
        intList = []
        for i in range(0, len(data_list), 4):
            intList.append(self.uint32_to_int(data_list[i:i+4]))
        return intList
    
    def uint32_to_int(self, data_list):
        return data_list[0]*256*256*256 + data_list[1]*256*256 + data_list[2]*256 + data_list[3]
        
    def int32_to_intList(self, data_list):
        intList = []
        for i in range(0, len(data_list), 4):
            intList.append(self.int32_to_int(data_list[i:i+4]))
        return intList

    def int32_to_int(self, data_list):
        if data_list[0] > 0x7f:
            data_list[0] = data_list[0] - 256
        return data_list[0]*256*256*256 + data_list[1]*256*256 + data_list[2]*256 + data_list[3]
    
    def float_to_hexstr(self, f):
        # convert float to hex
        # return str
        f = float(f)
        return hex(struct.unpack('<I', struct.pack('<f', f))[0]).ljust(10, '0')

    def hexstr_to_float(self, h):
        # convert hex to float
        # return float
        h = int(h, 16)
        return self.int_to_float(h)
    
    def int_to_float(self, i):
        return float(struct.unpack('<f', struct.pack('<I', i))[0])

    def intList_to_float(self, data_list):
        data = self.uint32_to_int(data_list)
        return self.int_to_float(data)

    def intList_to_floatList(self, data_list):
        datas = self.uint32_to_intList(data_list)
        floatList = []
        for data in datas:
            floatList.append(self.int_to_float(data))
        return floatList

    def uint32_to_floatList(self, data_list):
        floatList = []
        data_list = self.uint32_to_intList(data_list)
        for data in data_list:
            floatList.append(self.intList_to_float(data))
        return floatList

    def float_to_intList(self, f):
        hexstr = self.float_to_hexstr(f)[2:]
        return [int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16), int(hexstr[6:8], 16)]
        
    def intList_to_ASCII(self, data_list):
        data_raw = ''
        for data in data_list:
            data_raw += ('{:02X}'.format(data))
        data_ascii = (base64.b16decode(data_raw)).decode(errors='ignore').rstrip('\x00')
        return data_ascii


    def swap_endian(self, data_list):
        return list(reversed(data_list))

    def dBm_to_mW(self, dBm):
        return round(10**(dBm/10), 3)
    
    def mW_to_dBm(self, mW):
        return round(10*log(mW, 10), 3)

    def CMIS_u16IntList_to_float(self, data_list):
        data_list = self.swap_endian(data_list)
        data = self.uint16_to_int(data_list)
        exponent = ((data)>>11&0x1F)-24
        mantissa = data&0x7ff
        return mantissa*pow(10, exponent)

    def inphi_u16IntList_to_float(self, data_list):
        data_list = self.swap_endian(data_list)
        data = self.uint16_to_int(data_list)
        exponent = ((data&0xf800)>>11)-21
        mantissa = (data&0x7ff)/1023
        return mantissa*pow(10, exponent)
    
    def crest_add_cksum(self, list):
        list.append((0xFF - sum(list)&0xFF))
        return list

    def i32_to_u8_list(self, data:int):
        return [(data>>24)&0xFF, (data>>16)&0xFF, (data>>8)&0xFF, data&0xFF]

    def i16_to_u8_list(self, data:int):
        return [(data>>8)&0xFF, data&0xFF]

    def ASCII_to_u8_list(self, data:str):
        data_list = bytearray()
        data_list.extend(map(ord, data))
        return list(data_list)

    def file_u8_list_with(self, data_list, data, list_max_num):
        while(len(data_list)<list_max_num):
            data_list.append(data)
        return data_list

    def format_i2c_readout(self, start_addr, R_data):
        text = ''
        text += '   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F\n'
        text += '   -----------------------------------------------\n'
        white_space = '   ' * (start_addr % 16)
        formatted_data = white_space + \
            ''.join('{:02X} '.format(i)for i in R_data)
        start_msb = (start_addr // 16)
        for i in range(0, len(formatted_data), 16*3):
            text += (''.join('{:01X}'.format(start_msb % 16)) + 'x|'+formatted_data[i: i+48])
            start_msb += 1
            text += '\n'
        text += '   ***********************************************\n'
        return text
    
    def u8_list_to_hexstr(self, u8list) -> str:
        return ''.join(['{:02X}'.format(x) for x in u8list])


if __name__ == '__main__':
    cov = Data_convertor()
    # c = [0x4a, 0x89]
    # print(cov.inphi_u16IntList_to_float(c))
    a = -23
    print(cov.u16_to_u8_list(a))
    # print(pow(2, -11))
    