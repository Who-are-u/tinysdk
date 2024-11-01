# -*- encoding: utf-8 -*-
#@File    :   mediabase.py
#@Time    :   2024/09/04 21:41:18
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import logging
import os
import sys
from construct import BitsInteger, BitStruct, ByteSwapped, Int32ul, Struct
from abc import ABCMeta, abstractproperty,abstractmethod
from rom_features.trust_provisioning.trust_provisioning import OEM_PROV_FW,OEM_CKDFK
from rom_utils.keys_certs import AHABKeysCerts
from rom_utils.imggen.sbloader.sbloader3v1 import (
    SB3xCmdLoad, SB3xFile, SB3xImageType,SB3xCmdFillMemory, SB3xCmdConfigureMemory, SB3xCmdErase, SB3xCmdCopy
)

class FlashMemoryOption(metaclass=ABCMeta):
    """OptionStruct class."""
    
    @abstractmethod
    def __str__(self):
        pass

    @abstractproperty
    def option_st(self) -> Struct:
        """Struct to parse."""
        pass

    @abstractproperty
    def build(self) -> list:
        """Parse bytes.

        :param data_bytes: bytes to parse.
        :return Struct object with zero filled.
        """
        pass

class MemoryInterface(metaclass=ABCMeta):
    def __init__(self, free_sram_start):
        self.free_sram_start = free_sram_start

    @property
    def free_sram(self):
        return self.free_sram_start

    def init(self):
        pass

    def deinit(self):
        pass

    @abstractmethod
    def configure(self, configure_data: list, memory_id: int):
        pass

    @abstractmethod
    def erase(self, address: int, data_size: int, memory_id: int):
        pass

    @abstractmethod
    def erase_all(self, memory_id: int):
        pass

    @abstractmethod
    def write(self, start_address: int, file: str, memory_id: int):
        pass

    @abstractmethod
    def read(self, address: int, data_size: int, memory_id: int):
        pass


class IAPAPIMemoryInterface(MemoryInterface):
    def __init__(self, pyblhost, iap_api_buffer_address, iap_api_buffer_size=0x2000):
        super().__init__(iap_api_buffer_address)
        self.pybl = pyblhost
        self.iap_api_buffer_address = iap_api_buffer_address
        self.iap_api_buffer_size = iap_api_buffer_size

    def init(self):
        self.pybl.rom_api_iap_api_init(self.iap_api_buffer_address, self.iap_api_buffer_size)
        self.pybl.rom_api_iap_mem_init()

    def deinit(self):
        self.pybl.rom_api_iap_api_deinit()

    def configure(self, configure_data: list, memory_id: int):
        for i, config_word in enumerate(configure_data):
            self.pybl.rom_api_iap_mem_fill(self.free_sram_start + 4*i, 4, config_word)
        return self.pybl.rom_api_iap_mem_config(memory_id, self.free_sram_start)

    def erase(self, start_address: int, data_size: int, memory_id: int):
        return self.pybl.rom_api_iap_mem_erase(start_address, data_size, memory_id)

    def erase_all(self, memory_id: int):
        return self.pybl.rom_api_iap_mem_erase_all(memory_id)

    def write(self, start_address: int, file: str, memory_id: int):
        return self.pybl.rom_api_iap_mem_write(start_address, file, memory_id)

    def read(self, address: int, data_size: int, memory_id: int):
        return self.pybl.rom_api_iap_mem_read(address, data_size, memory_id)
    

class ISPMemoryInterface(MemoryInterface):
    def __init__(self, blhost, free_sram_start):
        super().__init__(free_sram_start)
        self.blhost = blhost

    def configure(self, configure_data: list, memory_id: int):
        for i, config_word in enumerate(configure_data):
            self.blhost.fill_memory(self.free_sram_start + 4*i, 4, config_word, 'word')
        return self.blhost.configure_memory(memory_id, self.free_sram_start)

    def erase(self, start_address: int, data_size: int, memory_id: int):
        return self.blhost.flash_erase_region(start_address, data_size, memory_id)

    def erase_all(self, memory_id: int):
        return self.blhost.flash_erase_all(memory_id)

    def write(self, start_address: int, file: str, memory_id: int):
        return self.blhost.write_memory(start_address, file, memory_id)

    def read(self, address: int, data_size: int, memory_id: int):
        return  self.blhost.read_memory(address, data_size, memory_id)


class SB3MemoryInterface(MemoryInterface):
    def __init__(self, blhost, free_sram_start, keys_certs):
        super().__init__(free_sram_start)
        self.blhost = blhost
        self.keys_certs = keys_certs

    def execute(self, sb_command_list):
        sb3v1 = SB3xFile(
            sb_command_list=sb_command_list,
            sbkek=OEM_CKDFK,
            keys_certs=self.keys_certs,
            kdk_access_rights=0,
            image_type=SB3xImageType.CIPHER_NORMAL_SB
        )
        self.blhost.receive_sb_file(sb3v1.sb3v1_image.bin_file)

    def configure(self, configure_data: list, memory_id: int):
        sb_command_list = []
        for i, config_word in enumerate(configure_data):
            sb_command_list.append(SB3xCmdFillMemory(self.free_sram_start + 4*i, 4, config_word))
        sb_command_list.append(SB3xCmdConfigureMemory(memory_id, self.free_sram_start))
        return self.execute(sb_command_list)
    
    def erase(self, start_address: int, data_size: int, memory_id: int):
        sb_command_list = []
        sb_command_list.append(SB3xCmdErase(start_address, data_size, memory_id))
        return self.execute(sb_command_list)

    def erase_all(self, memory_id: int):
        pass

    def write(self, start_address: int, file: str, memory_id: int):
        sb_command_list = []
        sb_command_list.append(SB3xCmdLoad(start_address, file, memory_id))
        return self.execute(sb_command_list)

    def read(self, address: int, data_size: int, memory_id: int):
        sb_command_list = []
        sb_command_list.append(SB3xCmdCopy(address, memory_id, self.free_sram_start, 0, data_size))
        return self.execute(sb_command_list)


class BootMedia(metaclass=ABCMeta):
    def __init__(self, memory_id: int, memory_interface: MemoryInterface):
        self.memory_id = memory_id
        self.memory_interface = memory_interface

    def set_memory_interface(self, memory_interface: MemoryInterface):
        self.memory_interface = memory_interface

    def init(self):
        return self.memory_interface.init()
    
    def deinit(self):
        return self.memory_interface.deinit()

    def configure(self, configure_data: list):
        return self.memory_interface.configure(configure_data, self.memory_id)

    def erase(self, start_address: int, data_size: int):
        return self.memory_interface.erase(start_address, data_size, self.memory_id)

    def erase_all(self):
        return self.memory_interface.erase_all(self.memory_id)

    def write(self, start_address: int, data_size: int):
        return self.memory_interface.write(start_address, data_size, self.memory_id)

    def read(self, address: int, data_size: int):
        return self.memory_interface.read(address, data_size, self.memory_id)
    

class BootMediaXspiNor(BootMedia):
    def __init__(self, memory_interface: MemoryInterface=None):
        super().__init__(0xb, memory_interface)


class BootMediaXspiNand(BootMedia):
    def __init__(self, memory_interface: MemoryInterface=None):
        super().__init__(0x102, memory_interface)


class BootMediaEmmc(BootMedia):
    def __init__(self, memory_interface: MemoryInterface=None):
        super().__init__(0x121, memory_interface)


class BootMediaSD(BootMedia):
    def __init__(self, memory_interface: MemoryInterface=None):
        super().__init__(0x112, memory_interface)


class BootMediaLpspi(BootMedia):
    def __init__(self, memory_interface: MemoryInterface=None):
        super().__init__(0x110, memory_interface)


class BootMediaSRAM(BootMedia):
    def __init__(self, memory_interface: MemoryInterface=None):
        super().__init__(0x0, memory_interface)

