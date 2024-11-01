# -*- encoding: utf-8 -*-
#@File    :   xspinor.py
#@Time    :   2024/03/28 16:32:07
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
from typing import Callable, Iterator, List, Optional, Dict, Any
from tinysdk.foo.typing import TinysdkEnum
from tinysdk.foo.xspi import EnumXspiInstance
from tinysdk.foo.exceptions import TinySDKValueError
from tinysdk.foo.media.mediabase import FlashMemoryOption

class EnumDeviceType(TinysdkEnum):
    QSPI_NOR_READ_SFDP_SDR = (0, "QSPI_NOR_READ_SFDP_SDR", "QSPI_NOR_READ_SFDP_SDR")
    QSPI_NOR_READ_SFDP_DDR = (1, "QSPI_NOR_READ_SFDP_DDR", "QSPI_NOR_READ_SFDP_DDR")
    HYPER_FLASH_1V8 = (2, "HYPER_FLASH_1V8", "HYPER_FLASH_1V8")
    HYPER_FLASH_3V0 = (3, "HYPER_FLASH_3V0", "HYPER_FLASH_3V0")  
    MXIC_OCTAL_NOR_DDR = (4, "MXIC_OCTAL_NOR_DDR", "MXIC_OCTAL_NOR_DDR")
    MXIC_OCTAL_NOR_SDR = (5, "MXIC_OCTAL_NOR_SDR", "MXIC_OCTAL_NOR_SDR")
    MICRON_OCTAL_NOR_DDR = (6, "MICRON_OCTAL_NOR_DDR", "MICRON_OCTAL_NOR_DDR")
    MICRON_OCTAL_NOR_SDR = (7, "MICRON_OCTAL_NOR_SDR", "MICRON_OCTAL_NOR_SDR") 
    ADESTO_OCTAL_NOR_DDR = (8, "ADESTO_OCTAL_NOR_DDR", "ADESTO_OCTAL_NOR_DDR")
    ADESTO_OCTAL_NOR_SDR = (9, "ADESTO_OCTAL_NOR_SDR", "ADESTO_OCTAL_NOR_SDR")

class EnumQueryPads(TinysdkEnum):
    PAD1 = (0, "PAD1", "PAD1")
    PAD2 = (1, "PAD2", "PAD2")
    PAD4 = (2, "PAD4", "PAD4")
    PAD8 = (3, "PAD8", "PAD8") 

class EnumCmdPads(TinysdkEnum):
    PAD1 = (0, "PAD1", "PAD1")
    PAD2 = (1, "PAD2", "PAD2")
    PAD4 = (2, "PAD4", "PAD4")
    PAD8 = (3, "PAD8", "PAD8") 

class EnumMiscMode(TinysdkEnum):
    PCS0 = (0, "PCS0", "PCS0")
    PCS1 = (1, "PCS1", "PCS1")
    PCS2 = (2, "PCS2", "PCS2")
    PCS3 = (3, "PCS3", "PCS3") 

class EnumMaxFrequency(TinysdkEnum):
    FREQ_50MHZ = (0, "FREQ_80MHZ", "FREQ_50MHZ")
    FREQ_60MHZ = (1, "FREQ_60MHZ", "FREQ_60MHZ")
    FREQ_80MHZ = (2, "FREQ_80MHZ", "FREQ_80MHZ")
    FREQ_100MHZ = (3, "FREQ_100MHZ", "FREQ_100MHZ") 
    FREQ_120MHZ = (5, "FREQ_120MHZ", "FREQ_120MHZ")
    FREQ_133MHZ = (5, "FREQ_133MHZ", "FREQ_133MHZ")
    FREQ_166MHZ = (6, "FREQ_166MHZ", "FREQ_166MHZ")
    FREQ_200MHZ = (7, "FREQ_200MHZ", "FREQ_200MHZ") 

class EnumFlashConnection(TinysdkEnum):
    PORTA = (0, "PORTA", "PORTA")
    PARALLEL = (1, "PARALLEL", "PARALLEL")
    PORTB = (2, "PORTB", "PORTB")
    PORTAB = (3, "PORTAB", "PORTAB") 

class EnumDriveStrength(TinysdkEnum):
    PCS0 = (0, "PCS0", "PCS0")
    PCS1 = (1, "PCS1", "PCS1")
    PCS2 = (2, "PCS2", "PCS2")
    PCS3 = (3, "PCS3", "PCS3") 

class EnumDqsGroup(TinysdkEnum):
    PRIMARY_GROUP = (0, "PRIMARY_GROUP", "PRIMARY_GROUP")
    SECONDARY_GROUP = (1, "SECONDARY_GROUP", "SECONDARY_GROUP")

class EnumPinMux(TinysdkEnum):
    PRIMARY_GROUP = (0, "PRIMARY_GROUP", "PRIMARY_GROUP")
    SECONDARY_GROUP = (1, "SECONDARY_GROUP", "SECONDARY_GROUP")

class EnumStatusOverride(TinysdkEnum):
    PCS0 = (0, "PCS0", "PCS0")
    PCS1 = (1, "PCS1", "PCS1")
    PCS2 = (2, "PCS2", "PCS2")
    PCS3 = (3, "PCS3", "PCS3") 

class EnumDummyCycle(TinysdkEnum):
    PCS0 = (0, "PCS0", "PCS0")
    PCS1 = (1, "PCS1", "PCS1")
    PCS2 = (2, "PCS2", "PCS2")
    PCS3 = (3, "PCS3", "PCS3")


class XspiOption(FlashMemoryOption):
    def __init__(self, 
        device_type:EnumDeviceType, 
        query_pads:EnumQueryPads,
        cmd_pads:EnumCmdPads,
        quad_mode_setting:int,
        misc_mode:int,
        max_freq:EnumMaxFrequency,
        flash_connection:EnumFlashConnection,
        drive_strength: int,
        dqs_pinmux_group:EnumDqsGroup,
        pinmux_group:EnumPinMux,
        status_override: int,
        dummy_cycles: int,
    ):
        self.device_type = device_type
        self.query_pads = query_pads
        self.cmd_pads = cmd_pads
        self.quad_mode_setting = quad_mode_setting
        self.misc_mode = misc_mode
        self.max_freq = max_freq
        self.flash_connection = flash_connection
        self.drive_strength = drive_strength
        self.dqs_pinmux_group = dqs_pinmux_group
        self.pinmux_group = pinmux_group
        self.status_override = status_override
        self.dummy_cycles = dummy_cycles

    @property
    def option_st(self) -> Struct:
        """ Define the struct of xspi option.

        """
        return Struct(
            'option0' / ByteSwapped(
                BitStruct(
                # [31:28] Tag, must be 0xC
                'tag' / BitsInteger(4),
                # [27:24] Option size, in terms of uint32_t, size = (option_size + 1) *4
                'option_size' / BitsInteger(4),
                # [23:20] Device type
                'device_type' / BitsInteger(4),
                # [19:16] SFDP read pads    
                'query_pads' / BitsInteger(4),
                # [15:12] Command pads 
                'cmd_pads' / BitsInteger(4),
                # [11:8] Quad mode setting
                'quad_mode_setting' / BitsInteger(4),
                # [7:4] miscellaneous mode
                'misc_mode' / BitsInteger(4),
                # [3:0] Maximum supported Frequency
                'max_freq' / BitsInteger(4),
                )
            ),

            'option1' / ByteSwapped(
                BitStruct(
                # [31:28] Flash connection option
                'flash_connection' / BitsInteger(4),
                # [27:24] The Drive Strength of xSPI Pads
                'drive_strength' / BitsInteger(4),
                # [23:20] The DQS Pinmux Group Selection
                'dqs_pinmux_group' / BitsInteger(4),
                # [19:16] The pinmux group selection
                'pinmux_group' / BitsInteger(4),
                # [15:8] Override status register value during device mode configuration
                'status_override' / BitsInteger(8),
                # [7:0] Dummy cycles before read
                'dummy_cycles' / BitsInteger(8),   
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
        option_st_obj.option0.tag= 0xC
        option_st_obj.option0.option_size = 1
        option_st_obj.option0.device_type = self.device_type.tag   
        option_st_obj.option0.query_pads = self.query_pads.tag
        option_st_obj.option0.cmd_pads = self.cmd_pads.tag
        option_st_obj.option0.quad_mode_setting = self.quad_mode_setting
        option_st_obj.option0.misc_mode = self.misc_mode
        option_st_obj.option0.max_freq = self.max_freq.tag

        option_st_obj.option1.flash_connection = self.flash_connection.tag
        option_st_obj.option1.drive_strength = self.drive_strength
        option_st_obj.option1.dqs_pinmux_group = self.dqs_pinmux_group.tag
        option_st_obj.option1.pinmux_group = self.pinmux_group.tag
        option_st_obj.option1.status_override = self.status_override
        option_st_obj.option1.dummy_cycles = self.dummy_cycles
        return list(struct.unpack_from(f"<{self.option_st.sizeof()//4}I", self.option_st.build(option_st_obj)))