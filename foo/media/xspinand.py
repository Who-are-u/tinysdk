# -*- encoding: utf-8 -*-
#@File    :   xspinand.py
#@Time    :   2024/09/04 21:41:25
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import logging
import os,sys
import time
from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional
from construct import Struct, Int64ul, Int32ul, ByteSwapped, BitStruct, BitsInteger
from tinysdk.foo.typing import TinysdkEnum
from tinysdk.foo.xspi import EnumXspiInstance
from tinysdk.foo.media.mediabase import FlashMemoryOption

@dataclass
class NandImageInfo():
    block_id: int
    block_count: int

class EnumAddressType(TinysdkEnum):
    AddressTypeByte= (0, "AddressTypeByte", "AddressTypeByte")
    AddressTypeBlock= (1, "AddressTypeBlock", "AddressTypeBlock")

class EnumSearchStride(TinysdkEnum):
    NandSearchStridePages_64= (0, "NandSearchStridePages_64", 64)
    NandSearchStridePages_128= (1, "NandSearchStridePages_128", 128)
    NandSearchStridePages_256= (2, "NandSearchStridePages_256", 256)
    NandSearchStridePages_32= (3, "NandSearchStridePages_32", 32)


class EnumSearchCount(TinysdkEnum):
    NandSearchCount_1= (1, "NandSearchCount_1", 1)
    NandSearchCount_2= (2, "NandSearchCount_2", 2)
    NandSearchCount_3= (3, "NandSearchCount_3", 3)
    NandSearchCount_4= (4, "NandSearchCount_4", 4)

@dataclass
class NandSearchInfo():
    search_stride: EnumSearchStride
    search_count: EnumSearchCount

    def __str__(self):
        return ".".join([str(self.search_stride), str(self.search_count)])

class EnumNandFreq(TinysdkEnum):
    NandFreq_80MHz = (0, "80MHz", "NandFreq_80MHz")
    NandFreq_100MHz= (1, "100MHz", "NandFreq_100MHz")
    NandFreq_120MHz= (2, "120MHz", "NandFreq_120MHz")
    NandFreq_133MHz= (3, "133MHz", "NandFreq_133MHz")
    NandFreq_166MHz= (4, "166MHz", "NandFreq_166MHz")
    NandFreq_200MHz= (5, "200MHz", "NandFreq_200MHz")
    NandFreq_50MHz= (6, "50MHz", "NandFreq_50MHz")
    NandFreq_30MHz= (7, "30MHz", "NandFreq_30MHz")

class EnumNandPageSize(TinysdkEnum):
    NandPageSize_2KB= (2, "2", "NandPageSize_2KB")
    NandPageSize_4KB= (4, "4", "NandPageSize_4KB")

class EnumNandPagePerBlock(TinysdkEnum):
    NandPagePerBlock_64= (0, "64", "NandPagePerBlock_64")
    NandPagePerBlock_128= (1, "128", "NandPagePerBlock_128")
    NandPagePerBlock_256= (2, "256", "NandPagePerBlock_256")
    NandPagePerBlock_32= (3, "32", "NandPagePerBlock_32")

class EnumNandPlane(TinysdkEnum):
    NandSinglePlane= (0, "SinglePlane", "NandSinglePlane")
    NandMutilPlane= (1, "MutilPlane", "NandMutilPlane")

class EnumNandFlashSize(TinysdkEnum):
    NandFlashSize_64MB= (0, "64", "NandFlashSize_64MB")
    NandFlashSize_128MB= (1, "128", "NandFlashSize_128MB")
    NandFlashSize_256MB= (2, "256", "NandFlashSize_256MB")
    NandFlashSize_512MB= (3, "512", "NandFlashSize_512MB")
    NandFlashSize_1024MB= (4, "1024", "NandFlashSize_1024MB")

class EnumNandTypes(TinysdkEnum):
    NandNandType_Quad= (0, "Quad", "NandNandType_Quad")
    NandNandType_Octal= (1, "Octal", "NandNandType_Octal")

class EnumNandManufacture(TinysdkEnum):
    ManufacturerID_NotDefine= (0x0, "ManufacturerID_NotDefine", "ManufacturerID_NotDefine")
    ManufacturerID_Micron= (0x2C, "ManufacturerID_Micron", "ManufacturerID_Micron")
    ManufacturerID_Macronix= (0xC2, "ManufacturerID_Macronix", "ManufacturerID_Macronix")
    ManufacturerID_Winbond= (0xEF, "ManufacturerID_Winbond", "ManufacturerID_Winbond")

class EnumNandEccFailureMask(TinysdkEnum):
    Nand_EccFailureNotDefine= (0x0, "Nand_EccFailureNotDefine", "Nand_EccFailureNotDefine")
    Nand_EccFailureMask= (0x30, "Nand_EccFailureMask", "Nand_EccFailureMask")
    Nand_EccFailureMaskNone= (0x00, "Nand_EccFailureMaskNone", "Nand_EccFailureMaskNone")

class EnumNandEccCheckMask(TinysdkEnum):
    Nand_EccCheckMaskNone= (0x00, "Nand_EccCheckMaskNone", "Nand_EccCheckMaskNone")
    Nand_EccCheckMask= (0x20, "Nand_EccCheckMask", "Nand_EccCheckMask")

class EnumExtendOptionSize(TinysdkEnum):
    OptionSize_0= (0, "0", "OptionSize_0")
    OptionSize_1= (1, "1", "OptionSize_0")


class NandOption(FlashMemoryOption):
    """Nand information class."""

    def __init__(self,
        max_freq : EnumNandFreq,
        page_size_in_kb : EnumNandPageSize,
        pages_per_block : EnumNandPagePerBlock,
        has_multiplanes : EnumNandPlane,
        flash_size : EnumNandFlashSize,
        device_type : EnumNandTypes,
        optiona_size : EnumExtendOptionSize,
        manufacturer_id : EnumNandManufacture,
        eccFailureMask : EnumNandEccFailureMask,
        eccCheckMask : EnumNandEccCheckMask ,      
    ):
        self.max_freq = max_freq
        self.page_size_in_kb = page_size_in_kb
        self.pages_per_block = pages_per_block
        self.has_multiplanes = has_multiplanes
        self.flash_size = flash_size
        self.device_type = device_type
        self.optiona_size = optiona_size
        self.manufacturer_id = manufacturer_id
        self.eccFailureMask = eccFailureMask
        self.eccCheckMask = eccCheckMask

    def __str__(self):
        """ return the description option, what it is.

        """
        return '-'.join([str(types) for var, types in self.__dict__.items()])

    def option_st(self) -> Struct:
        """Struct to parse."""
        return None
    
    def build(self)->list:
        """ build option words, return list of words

        """
        option_words = []
        option_words.append(
          ((self.max_freq.tag << 0)
          + (self.page_size_in_kb.tag  << 4)
          + (self.pages_per_block.tag  << 8)
          + (self.has_multiplanes.tag  << 12)
          + (self.flash_size.tag << 16)
          + (self.device_type.tag  << 20)
          + (self.optiona_size.tag  << 24)
          + (0xc << 28))
        ) 

        if self.optiona_size == EnumExtendOptionSize.OptionSize_1:
            option_words.append(
            ((self.manufacturer_id.tag << 0)
            + (self.eccFailureMask.tag << 8)
            + (self.eccCheckMask.tag  << 16))
            )
        return option_words
