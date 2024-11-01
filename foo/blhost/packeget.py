# -*- encoding: utf-8 -*-
#@File    :   relay.py
#@Time    :   2024/09/04 21:42:02
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import pytest,sys,os
import serial
import serial.tools.list_ports
import time
import logging 
import struct
from abc import ABCMeta, abstractproperty, abstractmethod
import crcmod.predefined
sys.path.append(os.path.join(os.path.dirname(__file__),"../"))
sys.path.append(os.path.join(os.path.dirname(__file__),"../../"))
sys.path.append(os.path.join(os.path.dirname(__file__),"../../../"))

class Packet(metaclass=ABCMeta):
    def __init__(self, package_type:int, payload_data:bytearray):
        self.package_type = package_type
        self.payload_data = payload_data

class PingPakage(Packet):
    def __init__(self):
        super().__init__(0xA6, None)

class SpecialFramePakage(Packet):
    def __init__(self, package_type:int):
        super().__init__(package_type, None)

class ACK(SpecialFramePakage):
    def __init__(self):
        super().__init__(0xA1)

class NAK(SpecialFramePakage):
    def __init__(self):
        super().__init__(0xA2)

class ABORT(SpecialFramePakage):
    def __init__(self):
        super().__init__(0xA3)

class FramePakage(Packet):
    def __init__(self, package_type:int, payload_data:bytearray):
        super().__init__(package_type, payload_data)
        
class ComandFramePakage(FramePakage):
    def __init__(self, command:int, param: list=[]):
        params = bytearray(param)
        if len(params) < 8:
            params = params + bytearray(8- len(params))

        payload_data=bytearray([command, 0, 0, len(param)+1]) + params
        super().__init__(0xA4, payload_data)

class DataFramePakage(FramePakage):
    def __init__(self, payload_data:bytearray):
        super().__init__(0xA5, payload_data)

class SerialPacket():
    def __init__(self, port = "COM7", baudrate = 115200, parity = "N", timeout =0.01):

        available_serial_ports=[]

        ports_list = list(serial.tools.list_ports.comports())  
        if len(ports_list) <= 0:
            logging.info("no serial ports available")
        else:
            for comport in ports_list:
                available_serial_ports.append(list(comport)[0])

        if port not in available_serial_ports:
            raise ValueError(f"{port} is not available")       
                
        ser = serial.Serial("COM7", 115200, 8, "N")    
        if ser.isOpen():                      
            logging.info(f"open {port} {baudrate} {parity}") 
        else:
            raise ValueError("serial port is not available") 
        self.ser= ser
        self.timeout = timeout

    def read(self, length: int, timeout:int=100):
        package = bytearray()
        timeout_count = 0
        while(len(package) < length and timeout_count < timeout):
            if self.ser.in_waiting > 0:
                byte = self.ser.read(1)
                package.append(byte[0])
            else:
                time.sleep(self.timeout)
            timeout_count = timeout_count + 1
        return package

    def hear_check(self, header: bytearray):
        assert len(header) == 2
        assert header[0] == 0x5a
        assert header[1] in [0xa1, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7]
        return header[1]

    def crc16_check(self, data: bytearray):
        crc16_xmodem = crcmod.predefined.mkPredefinedCrcFun('xmodem')
        crc16_xmodem_checksum = crc16_xmodem(bytes(data))
        return crc16_xmodem_checksum
        
    def read_packet(self):
        header = self.read(2)
        package_type = self.hear_check(header)

        if package_type in [0xa1,0xa2,0xa3]:
            logging.info('receive<-: ' + ','.join([f"{x:#04x}" for x in list(header)]))
            return package_type, None
        elif package_type in [0xa7]:
            payload_data = self.read(6)
            checksum_crc16 = self.read(2)
            temp_data = bytearray()
            temp_data = header + payload_data
            logging.info('receive<-: ' + ','.join([f"{x:#04x}" for x in list(header + payload_data + checksum_crc16)]))
        else:
            logging.info("command or data package.")
            payload_size = self.read(2)
            payload_size_, = struct.unpack_from("<H", bytes(payload_size))
            checksum_crc16 = self.read(2)
            payload_data = self.read(payload_size_)
            temp_data = bytearray()
            temp_data = header + payload_size + payload_data
            logging.info('receive<-: ' + ','.join([f"{x:#04x}" for x in list(header + payload_size + checksum_crc16 + payload_data)]))

        checksum_crc16_calcu, = struct.unpack_from("<H", bytes(checksum_crc16))
        assert checksum_crc16_calcu == self.crc16_check(temp_data)
        return package_type, payload_data

    def write_packet(self, package_type, payload_data=None):
        assert package_type in [0xa1,0xa2,0xa3,0xa4,0xa5,0xa6]
        packet = bytearray()
        packet.append(0x5a)
        packet.append(package_type)
        if package_type in [0xa4,0xa5]:
            payload_size = len(payload_data)
            packet = packet + bytearray(struct.pack("<H", payload_size))
            temp_data = packet + payload_data
            checksum_crc16 = self.crc16_check(temp_data)
            packet = packet + bytearray(struct.pack("<H", checksum_crc16)) + payload_data
        logging.info('send->: ' + ','.join([f"{x:#04x}" for x in list(packet)]))
        self.ser.write(bytes(packet))

class BlhostCommand(metaclass=ABCMeta):
    def __init__(self, serial, command: int, send: bool=False, resp: bool=False):
        self.serial = serial
        self.send = send
        self.resp = resp
        self.command = command

    def execute(self, params:list=[]):
        """Step1. ping"""
        ping = PingPakage()
        self.serial.write_packet(ping.package_type, ping.payload_data)
        package_type, payload_data = self.serial.read_packet()

        if self.send:
            """Get Maxium package size"""
            cmd = ComandFramePakage(0x7, [11])
            self.serial.write_packet(cmd.package_type, cmd.payload_data)
            package_type, payload_data = self.serial.read_packet()
            package_type, payload_data = self.serial.read_packet()  
            ack = ACK()
            self.serial.write_packet(ack.package_type, ack.payload_data)   

            """ extract maxium package size from payload_data.
            """
            max_package_size = 512

        cmd = ComandFramePakage(self.command, params)
        self.serial.write_packet(cmd.package_type, cmd.payload_data)
        package_type, payload_data = self.serial.read_packet()
        package_type, payload_data = self.serial.read_packet()
        ack = ACK()
        self.serial.write_packet(ack.package_type, ack.payload_data)

        if self.send:
            data = DataFramePakage(bytearray([0x11,0x22,0x33,0x44]))
            self.serial.write_packet(data.package_type, data.payload_data)
            package_type, payload_data = self.serial.read_packet()
            ack = ACK()
            self.serial.write_packet(ack.package_type, ack.payload_data)
        
        if self.resp:
            package_type, payload_data = self.serial.read_packet()
            ack = ACK()
            self.serial.write_packet(ack.package_type, ack.payload_data)


class GetProperty(BlhostCommand):
    def __init__(self, serial):
        super().__init__(serial, 0x7)

class WriteMemory(BlhostCommand):
    def __init__(self, serial):
        super().__init__(serial, 0x4, send=True)


class BlhostClient():
    def __init__(self, port = "COM7", baudrate = 115200, parity = "N"):
        self.ser = SerialPacket(port, baudrate, parity)

    def get_property(self, tag: int):
        GetProperty(self.ser).execute([tag])

    def write_memory(self, address: int, size: int, mem_id: int):
        WriteMemory(self.ser).execute([1])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='\n%(asctime)s - %(filename)s - %(levelname)s [Line %(lineno)d]\n%(message)s'
    )

    blhost = BlhostClient()
    blhost.write_memory(1,1,1)





        