# -*- encoding: utf-8 -*-
#@File    :   lpspi.py
#@Time    :   2024/03/28 16:31:56
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import os
import logging
import time
from abc import ABCMeta, abstractproperty, abstractmethod
import struct
from construct import Struct, Int64ul, Int32ul, ByteSwapped, BitStruct, BitsInteger
import sys
from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional,Dict
from tinysdk.foo.typing import TinysdkEnum
from tinysdk.foo.media.mediabase import FlashMemoryOption

class EnumSpiInstance(TinysdkEnum):
    LPSPI0 = (0, "LPSPI0", "LPSPI0")
    LPSPI1 = (1, "LPSPI1", "LPSPI1")
    LPSPI2 = (2, "LPSPI2", "LPSPI2")
    LPSPI3 = (3, "LPSPI3", "LPSPI3")  
    LPSPI4 = (4, "LPSPI4", "LPSPI4")
    LPSPI5 = (5, "LPSPI5", "LPSPI5")
    LPSPI6 = (6, "LPSPI6", "LPSPI6")
    LPSPI7 = (7, "LPSPI7", "LPSPI7") 
    LPSPI8 = (8, "LPSPI8", "LPSPI8")
    LPSPI9 = (9, "LPSPI9", "LPSPI9")

class EnumSpiPcs(TinysdkEnum):
    PCS0 = (0, "PCS0", "PCS0")
    PCS1 = (1, "PCS1", "PCS1")
    PCS2 = (2, "PCS2", "PCS2")
    PCS3 = (3, "PCS3", "PCS3") 


class LpspiOption(FlashMemoryOption):
    def __init__(self,
        spi_index:EnumSpiInstance, 
        pcs_index:EnumSpiPcs,
        memory_type:int,
        memory_size:int, 
        sector_size:int,
        page_size:int, 
        spi_speed:int,   
    ):
        self.spi_index = spi_index
        self.pcs_index = pcs_index
        self.memory_type = memory_type
        self.memory_size = memory_size
        self.sector_size = sector_size
        self.page_size = page_size
        self.spi_speed = spi_speed


    @property
    def option_st(self) -> Struct:
        return Struct(
            'option0' / ByteSwapped(
                BitStruct(
                    'tag'/ BitsInteger(4),          # Bit[31~28]
                    'option_size'/BitsInteger(4),   # Bit[27~24]
                    'spi_index'/BitsInteger(4),     # Bit[23~20]
                    'pcs_index'/BitsInteger(4),     # Bit[19~16]
                    'memory_type'/BitsInteger(4),   # Bit[15~12]
                    'memory_size'/BitsInteger(4),   # Bit[11~08]
                    'sector_size'/BitsInteger(4),   # Bit[07~04]
                    'page_size'/ BitsInteger(4),    # Bit[03~00] 
                )
            ),
            'option1' / ByteSwapped(
                BitStruct(
                    'reserved'/ BitsInteger(28),    # Bit[31~04]
                    'spi_speed'/BitsInteger(4),     # Bit[03~00]
                )
            )
        )

    def __str__(self):
        """ return the description option, what it is.

        """
        return '-'.join([str(types) for var, types in self.__dict__.items()])
 
    def build(self)->list:
        """ build option words, return list of words

        """
        option_st_obj = self.option_st.parse(bytes([0] * self.option_st.sizeof()))
        option_st_obj.option0.tag= 0xc
        option_st_obj.option0.option_size = 1
        option_st_obj.option0.spi_index = self.spi_index.tag    
        option_st_obj.option0.pcs_index = self.pcs_index.tag    
        option_st_obj.option0.memory_type = self.memory_type
        option_st_obj.option0.memory_size = self.memory_size
        option_st_obj.option0.sector_size = self.sector_size
        option_st_obj.option0.page_size = self.page_size  
        option_st_obj.option1.spi_speed = self.spi_speed
        
        return list(struct.unpack_from(f"<{self.option_st.sizeof()//4}I", self.option_st.build(option_st_obj)))

