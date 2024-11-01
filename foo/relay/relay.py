# -*- encoding: utf-8 -*-
#@File    :   relay.py
#@Time    :   2024/09/04 21:42:02
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import pytest
import serial
import serial.tools.list_ports
import time
import logging 
from abc import ABCMeta, abstractproperty, abstractmethod


class Relay(metaclass=ABCMeta):
    def __init__(self, port:str="COM1", baudrate: int=115200, parity:str="N", name:str=""):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.name = name
        self.ser= None
        self.available_serial_ports = []

        ports_list = list(serial.tools.list_ports.comports())  
        if len(ports_list) <= 0:
            logging.info("no serial ports available")
        else:
            logging.info("available serial ports")
            for comport in ports_list:
                self.available_serial_ports.append(list(comport)[0])

    def connect(self, timeout:int=50):
        if self.port not in self.available_serial_ports:
            raise ValueError(f"{self.port} is not available")       
                
        ser = serial.Serial(self.port, self.baudrate, 8, self.parity, timeout=timeout, stopbits=1)    
        if ser.isOpen():                      
            logging.info(f"open {self.port} {self.baudrate} {self.parity}") 
        else:
            raise ValueError("serial port is not available")  
        self.ser= ser

    def disconnect(self):
        """Disconnect from the target
        
        :param :None
        
        :returns: None
        """
        self.ser.close()

    def execute(self, command):
        """Private method to write serial
        
        :param bytes command: The actual command to write into serial, such as `[0xAA,0x5A,0x00,0x00,0x00,0xFF]`.
        
        :returns: None
        """
        logging.info(''.join('%#02x '%e for e in command))
        self.ser.write(bytes(command))


    @abstractmethod
    def single(self, channel:int, on:bool = True):
        pass

class LPC800(Relay):
    """ Provide interface for LPC800 assitant board which could be used to control up to 14 relays.
    """
    def __init__(self, port="COM1", baudrate=115200, parity='N'):
        """Build a connection to target through the given port and its attribites
        
        :param str port: The serial port name, such as COMx, x could be 1, 2, 3, etc.`"COM1"` by defaut.
        
        :param int baudrate: The baudrate. `9600` by defaut.
        
        :param char parity: The parity could be `'N'` ,`'O'` or `'N'` by defaut.
        
        :returns: None
        """
        super().__init__(port, baudrate, parity, "LPC800")


    def single(self, channel, on=False):
        """Turn it to be `"on"`, then turn it to be `"off"` after 1 second, Could be used to MCU reset senarios generally.
        
        :param int channel: The channel id, could be `1,2,..14`.
        
        :returns: None
        """
        if channel < 1 or channel > 14:
            raise ValueError(f"{channel} is not supported")
        
        command = f"IN{channel}_{'HIGH' if on else 'LOW'}\r\n" 
        self.execute(command.encode())
        
class HC1116(Relay):
    """ Provide serveral interfaces for HC1116 module which is used to control 16 relays on it. Please notes that not all commands supported are implemented fully. 
    """
    def __init__(self, port="COM1", baudrate=9600, parity='N', address=0):
        """Build a connection to target through the given port and its attribites
        
        :param str port: The serial port name, such as COMx, x could be 1, 2, 3, etc.`"COM1"` by defaut.
        
        :param int baudrate: The baudrate. `9600` by defaut.
        
        :param char parity: The parity could be `'N'` ,`'O'` or `'N'` by defaut.
        
        :param int address: The address could be set by command. `0` by defaut. 

        :returns: None
        """
        super().__init__(port, baudrate, parity, "HC1116")
        self.address = address
        self.command_set = {
            "single"     : [0xAA,0x5A,0x00,0x00,0x00,0xFF],
            "more"   : [0xAA,0x5A,0x00,0xFD,0x00,0xFF],
            "open_all"      : [0xAA,0x5A,0x00,0xFF,0x00,0xFF],
            "close_all"     : [0xAA,0x5A,0x00,0xFE,0x00,0xFF],
            "timer"     : [0xAA,0x5A,0x00,0x00,0x00,0xFF],
            "status"    : [0xAA,0x5A,0x00,0xFC,0x00,0xFF]
        }

    def get_state(self, channel:int):
        """Turn the specified channel to be `"on"` and `"off"
        
        :param int channel: The channel id, could be `0,1,2,..15`
        
        :param boolean on: `False` means `"off"` whereas `True` indicates `"on"`
        
        :returns: None
        """
        if channel < 0 or channel > 15:
            raise ValueError(f"{channel} should be between 0 and 15")

        self.ser.read(self.ser.in_waiting)
        command = self.command_set["status"]
        self.execute(bytes(command))
        read_bytes = self.ser.read(6)
        status = int.from_bytes(read_bytes[4:6],"big")
        if ((0x1<<(15 - channel))&status) != 0:
            return True
        else:
            return False
              
    def single(self, channel:int, on:bool = True):
        """Turn the specified channel to be `"on"` and `"off"
        
        :param int channel: The channel id, could be `0,1,2,..15`
        
        :param boolean on: `False` means `"off"` whereas `True` indicates `"on"`
        
        :returns: None
        """
        if channel < 0 or channel > 15:
            raise ValueError(f"{channel} should be between 0 and 15")

        state = self.get_state(channel)
        if state == on:
            return

        command = self.command_set["single"]
        command[2] = self.address 
        command[3] = channel << 4 | 0x01 if on else channel << 4 | 0x00
        self.execute(bytes(command))
         
    def timer(self, channel):
        """Turn it to be `"on"`, then turn it to be `"off"` after 1 second, Could be used to MCU reset senarios generally.
        
        :param int channel: The channel id, could be `0,1,2,..15`.
        
        :returns: None
        """
        if channel < 0 or channel > 15:
            raise ValueError(f"{channel} should be between 0 and 15")
        
        command = self.command_set["timer"]
        command[2] = self.address 
        command[3] = channel << 4 | 0x02
        self.execute(bytes(command))
               
    def more(self, channel_list=[]):
        """Allow to trigger the head eight channels at once. The channels excluded in `channel_list` would be `"off"` by default .
        
        :param list channel_list: The channels are to be `"on"`, e.g., `[1,2]`. channel 1 and 2 is to be `"on"`, othes will set to be `"off"`.
        
        :returns: None
        """
        command = self.command_set["more"]
        command[2] = self.address
        for index, channel in enumerate(channel_list):
            if channel >= 8:
                raise ValueError("channel must be between 0 and 8")
            command[4] |= 0x01 << channel
        self.execute(bytes(command))
        
    def all(self, on=False):
        """Reset the total of 16 channels to be `"on"` or `"off"` according to `on`
        
        :param boolean on: `False` means `"off"` whereas `True` indicates `"on"`
        
        :returns: None
        """
        command = self.command_set["open_all"] if on else self.command_set["close_all"]
        command[2] = self.address 
        self.execute(bytes(command))
 
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='\n%(asctime)s - %(filename)s - %(levelname)s [Line %(lineno)d]\n%(message)s'
    )
    relay = HC1116(port="COM6", baudrate=9600, parity='N')

    relay.connect()
    relay.get_state(0)

    relay.single(channel=0, on=True)
    relay.single(channel=0, on=True)
    relay.single(channel=0, on=True)
    relay.single(channel=0, on=True)
    relay.get_state(0)
    time.sleep(1)
    relay.single(channel=0, on=False)
    relay.get_state(0)
    
    relay.all(on=True)
    relay.get_state(0)
    time.sleep(1)
    relay.all(on=False)
    relay.get_state(0)
    time.sleep(1)
    relay.more([1, 2, 3, 4, 5, 6, 7])
    
    relay.timer(channel=0)
        