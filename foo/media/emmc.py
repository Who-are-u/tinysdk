# -*- encoding: utf-8 -*-
#@File    :   emmc.py
#@Time    :   2024/03/28 16:31:45
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
from tinysdk.foo.media.mediabase import FlashMemoryOption

class EnumPwrDown(TinysdkEnum):
    """
        Mode	            Data Rate	Bus Width	Frequency	Max Data Transfer (x8)
        ================================================================================
        Backward Compatible	Single	    x1, x4, x8	0-26 MHz	26 MB/s
        ================================================================================
        High Speed SDR	    Single	    x1, x4, x8	0-52 MHz	52 MB/s
        ================================================================================
        High Speed DDR	    Dual	    x4, x8	    0-52 MHz	104 MB/s
        ================================================================================
        HS200	            Single	    x4, x8	    0-200 MHz	200 MB/s
        ================================================================================
        HS400	            Dual	    x8	        0-200 MHz	400 MB/s
        ================================================================================

    """
    kSDMMC_PWR_DOWN_20MS = (0, "kSDMMC_PWR_DOWN_20MS", "kSDMMC_PWR_DOWN_20MS")
    kSDMMC_PWR_DOWN_10MS = (1, "kSDMMC_PWR_DOWN_10MS", "kSDMMC_PWR_DOWN_10MS")
    kSDMMC_PWR_DOWN_5MS = (2, "kSDMMC_PWR_DOWN_5MS", "kSDMMC_PWR_DOWN_5MS")
    kSDMMC_PWR_DOWN_2D5MS = (3, "kSDMMC_PWR_DOWN_2D5MS", "kSDMMC_PWR_DOWN_2D5MS")

class EnumPwrUp(TinysdkEnum):
    kSDMMC_PWR_UP_5MS = (0, "kSDMMC_PWR_UP_5MS", "kSDMMC_PWR_UP_5MS")
    kSDMMC_PWR_UP_2D5MS = (1, "kSDMMC_PWR_UP_2D5MS", "kSDMMC_PWR_UP_2D5MS")

class EnumuSDHCInsance(TinysdkEnum):
    kSDMMCInstance0 = (0, "kSDMMCInstance0", "kSDMMCInstance0")
    kSDMMCInstance1 = (1, "kSDMMCInstance1", "kSDMMCInstance1")

class EnumDataBusWidth(TinysdkEnum):
    """ JESD84-B51.pdf BUS_WIDTH [183]
    Bus Width, Normal or DDR mode and Strobe mode (for HS400) are defined through BUS_WIDTH 
    register

    HS_TIMING must be set to “0x1” before setting BUS_WIDTH for dual data rate operation 
    (values 5 or 6)
    
    The fowlowing mode defines the Bus Mode Selection
    """
    kMMC_DataBusWidth1bit = (0, "kMMC_DataBusWidth1bit", "kMMC_DataBusWidth1bit")
    kMMC_DataBusWidth4bit = (1, "kMMC_DataBusWidth4bit", "kMMC_DataBusWidth4bit")
    kMMC_DataBusWidth8bit = (2, "kMMC_DataBusWidth8bit", "kMMC_DataBusWidth8bit")
    kMMC_DataBusWidth4bitDDR = (5, "kMMC_DataBusWidth4bitDDR", "kMMC_DataBusWidth4bitDDR")
    kMMC_DataBusWidth8bitDDR = (6, "kMMC_DataBusWidth8bitDDR", "kMMC_DataBusWidth8bitDDR")

class EnumSpeedTiming(TinysdkEnum):    
    """JESD84-B51.pdf  HS_TIMING [185]
    0x0 Selecting backwards compatibility interface timing 
    0x1 High Speed 
    0x2 HS200 
    0x3 HS400
    """
    kMMC_HighSpeedTimingNone = (0, "kMMC_HighSpeedTimingNone", "kMMC_HighSpeedTimingNone")
    kMMC_HighSpeedTiming = (1, "kMMC_HighSpeedTiming", "kMMC_HighSpeedTiming")
    kMMC_HighSpeed200Timing = (2, "kMMC_HighSpeed200Timing", "kMMC_HighSpeed200Timing")
    kMMC_HighSpeed400Timing = (3, "kMMC_HighSpeed400Timing", "kMMC_HighSpeed400Timing")
    
class EnumBootPartitionEnable(TinysdkEnum):
    """ 'boot_partition_enable' is used to configure BOOT_PARTITION_ENABLE field in register PARTITION_CONFIG
        It supports the following types of modes:
    """
    kSDMMCBootPartitionEnable_NoBootEnable = (0, "kSDMMCBootPartitionEnable_NoBootEnable", "kSDMMCBootPartitionEnable_NoBootEnable")
    kSDMMCBootPartitionEnable_BootAreaPartition1 = (1, "kSDMMCBootPartitionEnable_BootAreaPartition1", "kSDMMCBootPartitionEnable_BootAreaPartition1")
    kSDMMCBootPartitionEnable_BootAreaPartition2 = (2, "kSDMMCBootPartitionEnable_BootAreaPartition2", "kSDMMCBootPartitionEnable_BootAreaPartition2")
    kSDMMCBootPartitionEnable_UserAreaPartition  = (7, "kSDMMCBootPartitionEnable_UserAreaPartition", "kSDMMCBootPartitionEnable_UserAreaPartition")

class EnumPartitionAcess(TinysdkEnum):
    """ 'partition_access' is used to configure PARTITION_ACCESS field in register PARTITION_CONFIG
        User select partition to access,It supports the following types of modes: 
    """
    kSDMMCPartitionAcess_NoPartition = (0, "kSDMMCPartitionAcess_NoPartition", "kSDMMCPartitionAcess_NoPartition")
    kSDMMCPartitionAcess_BootAreaPartition1 = (1, "kSDMMCPartitionAcess_BootAreaPartition1", "kSDMMCPartitionAcess_BootAreaPartition1")
    kSDMMCPartitionAcess_BootAreaPartition2 = (2, "kSDMMCPartitionAcess_BootAreaPartition2", "kSDMMCPartitionAcess_BootAreaPartition2")
    kSDMMCPartitionAcess_RPMBPartition = (3, "kSDMMCPartitionAcess_RPMBPartition", "kSDMMCPartitionAcess_RPMBPartition")
    kSDMMCPartitionAcess_GeneralPurposePartition1 = (4, "kSDMMCPartitionAcess_GeneralPurposePartition1", "kSDMMCPartitionAcess_GeneralPurposePartition1")
    kSDMMCPartitionAcess_GeneralPurposePartition2 = (5, "kSDMMCPartitionAcess_GeneralPurposePartition2", "kSDMMCPartitionAcess_GeneralPurposePartition2")
    kSDMMCPartitionAcess_GeneralPurposePartition3 = (6, "kSDMMCPartitionAcess_GeneralPurposePartition3", "kSDMMCPartitionAcess_GeneralPurposePartition3")
    kSDMMCPartitionAcess_GeneralPurposePartition4 = (7, "kSDMMCPartitionAcess_GeneralPurposePartition4", "kSDMMCPartitionAcess_GeneralPurposePartition4")

class EnumBootEnablement(TinysdkEnum):
    """ 'boot_config_enable' is used to enable boot configuration, all about boot configuration e.g.: boot_ack,boot_partition_enable,boot_bus_width
    reset_boot_bus_conditions,boot_mode will not be configured unless boot_config_enable is enabled
    It supports the following types of modes: 
    
    'boot_ack' is used to configure BOOT_ACK field in register PARTITION_CONFIG
    If boot_ack was enable, eMMC will acknowledge '010' via DAT0 to uSDHC hoste in 50 miliesecdonds  during boot operation
    It supports the following types of modes: 
    
    "reset_boot_bus_conditions" is used to configure RESET_BOOT_BUS_CONDITIONS field in the register BOOT_BUS_CONDITIONS
        after quit from Boot mode. the bus can be resevered for configured mode or Backward Compatible SDR x1 (kMMC_BootModeSDRAndBackwardTiming)
        It supports the following types of modes: 

    """  
    kMMC_Disable = (0, "kMMC_Disable", "kMMC_Disable")
    kMMC_Enable  = (1, "kMMC_Enable", "kMMC_Enable")
    
class EnumBootMode(TinysdkEnum):
    """ "boot_mode" is used to configure BOOT_MODE field in the register BOOT_BUS_CONDITIONS.
            It supports the following three types of modes:
            
            kMMC_BootModeSDRAndBackwardTiming
            kMMC_BootModeSDRAndHighspeed = 1
            kMMC_BootModeDDR = 2
            Note that : HS200 and HS400 is not supported during BOOT operation
        
    0x0 : Use single data rate + backward compatible timings in boot operation (default) 
    0x1 : Use single data rate + High Speed timings in boot operation mode 
    0x2 : Use dual data rate in boot operation 
    0x3 : Reserved 
    """
    kMMC_BootModeSDRAndBackwardTiming = (0, "kMMC_BootModeSDRAndBackwardTiming", "kMMC_BootModeSDRAndBackwardTiming")
    kMMC_BootModeSDRAndHighspeed = (1, "kMMC_BootModeSDRAndHighspeed", "kMMC_BootModeSDRAndHighspeed")
    kMMC_BootModeDDR = (2, "kMMC_BootModeDDR", "kMMC_BootModeDDR")

class EnumBootBusWidth(TinysdkEnum):
    """ "boot_bus_width" is used to configure BOOT_BUS_WIDTH field in the register BOOT_BUS_CONDITIONS
        It supports the following three types of modes:
        
        kMMC_BootBusWidthX1 = 0, if "boot_mode" is configure ddr(kMMC_BootModeDDR), it represents X4
        kMMC_BootBusWidthX4 = 1
        kMMC_BootBusWidthX8 = 2
        
    0x0 : x1 (sdr) or x4 (ddr) bus width in boot operation mode (default) 
    0x1 : x4 (sdr/ddr) bus width in boot operation mode 
    0x2 : x8 (sdr/ddr) bus width in boot operation mode 
    0x3 : Reserved
    """
    kMMC_BootBusWidthX1 = (0, "kMMC_BootBusWidthX1", "kMMC_BootBusWidthX1")
    kMMC_BootBusWidthX4 = (1, "kMMC_BootBusWidthX4", "kMMC_BootBusWidthX4")
    kMMC_BootBusWidthX8 = (2, "kMMC_BootBusWidthX8", "kMMC_BootBusWidthX8")

class EnumPwrPority(TinysdkEnum):
    """ """
    kMMC_Low = (0, "kMMC_Low", "kMMC_Low")
    kMMC_High = (1, "kMMC_High", "kMMC_High")

class EnumBootConfigEnablement(TinysdkEnum):
    """.."""
    kMMC_Disable= (0, "kMMC_Disable", "kMMC_Disable")
    kMMC_Enable = (1, "kMMC_Enable", "kMMC_Enable")

class EnumBootAck(TinysdkEnum):
    """ """
    kMMC_Disable = (0, "kMMC_Disable", "kMMC_Disable")
    kMMC_Enable = (1, "kMMC_Enable", "kMMC_Enable")

class EnumEnablePwrCycle(TinysdkEnum):
    """ """
    kMMC_Disable = (0, "kMMC_Disable", "kMMC_Disable")
    kMMC_Enable = (1, "kMMC_Enable", "kMMC_Enable")

class EnumResetBootBusConditions(TinysdkEnum):
    """ """
    kMMC_BootBusCondition1 = (0, "kMMC_BootBusCondition1", "kMMC_BootBusCondition1")
    kMMC_BootBusCondition2 = (1, "kMMC_BootBusCondition2", "kMMC_BootBusCondition2")


class EmmcOption(FlashMemoryOption):

    def __init__(self,
        partition_access: EnumPartitionAcess,
        boot_partition_enable: EnumBootPartitionEnable,
        boot_bus_width: EnumBootBusWidth,
        timing_interface: EnumSpeedTiming,
        bus_width: EnumDataBusWidth,
        boot_mode: EnumBootMode,
        reset_boot_bus_conditions: EnumResetBootBusConditions,
        boot_ack: EnumBootAck,
        boot_config_enable: EnumBootConfigEnablement ,
        power_down_time: EnumPwrDown, 
        power_polarity: EnumPwrPority,
        power_up_time: EnumPwrUp,
        enable_power_cycle: EnumEnablePwrCycle,
        instance: EnumuSDHCInsance ,   
    ):
        self.partition_access= partition_access
        self.boot_partition_enable=boot_partition_enable
        self.boot_bus_width= boot_bus_width
        self.timing_interface= timing_interface
        self.bus_width=bus_width
        self.boot_mode= boot_mode
        self.reset_boot_bus_conditions= reset_boot_bus_conditions
        self.boot_ack= boot_ack
        self.boot_config_enable= boot_config_enable 
        self.power_down_time= power_down_time 
        self.power_polarity=power_polarity
        self.power_up_time=power_up_time
        self.enable_power_cycle=enable_power_cycle
        self.instance=instance

    @property
    def option_st(self) -> Struct:
        return Struct(
            'option0' / ByteSwapped(
                BitStruct(
                    # EMMC configuration block tag, must be 0xC
                    'tag' / BitsInteger(4),                        # [31:28]   
                    'rsv4' / BitsInteger(1),                       # [27]
                    # Select EMMC partition which the flashloader write image to
                    'partition_access' / BitsInteger(3),           # [26:24]
                    'rsv3' / BitsInteger(1),                       # [23]
                    'boot_partition_enable' / BitsInteger(3),      # [22:20]
                    'rsv2' / BitsInteger(2),                       # [19:18]
                    'boot_bus_width' / BitsInteger(2),             # [17:16]
                    'timing_interface' / BitsInteger(4),           # [15:12]
                    'bus_width' / BitsInteger(4),                  # [11:8]
                    'rsv1' / BitsInteger(2),                       # [7:6]
                    'boot_mode' / BitsInteger(2),                  # [5:4]
                    'reset_boot_bus_conditions' / BitsInteger(1),  # [3]
                    'boot_ack' / BitsInteger(1),                   # [2]
                    'rsv0' / BitsInteger(1),                       # [1]
                    'boot_config_enable' / BitsInteger(1),         # [0]
                )
            ),
            'option1' / ByteSwapped(
                BitStruct(
                    'rsv_driver_strength' / BitsInteger(4),        # [31:28]  
                    'rsv2' / BitsInteger(2),                       # [27:26]
                    'power_down_time' / BitsInteger(2),            # [25:24]
                    'power_polarity' / BitsInteger(1),             # [23]
                    'rsv1' / BitsInteger(2),                       # [22:21]
                    'power_up_time' / BitsInteger(1),              # [20]
                    'enable_power_cycle' / BitsInteger(1),         # [19]
                    'enable_1v8' / BitsInteger(1),                 # [18]
                    'rsv_perm_boot_config_prot' / BitsInteger(2),  # [17:16]
                    'rsv0' / BitsInteger(10),                      # [15:6]
                    'rsv_perm_config_enable' / BitsInteger(2),     # [5:4]
                    'instance' / BitsInteger(4),                   # [3:0]
                )
            )
        )

    def __str__(self):
        """ return the description option, what it is.

        """
        return '\n'.join([str(types) for var, types in self.__dict__.items()])
 
    def build(self)->list:
        """ build option words, return list of words

        """
        option_st_obj = self.option_st.parse(bytes([0] * self.option_st.sizeof()))
        option_st_obj.option0.tag = 0xc                                             
        option_st_obj.option0.partition_access = self.partition_access.tag                                 
        option_st_obj.option0.boot_partition_enable = self.boot_partition_enable.tag                              
        option_st_obj.option0.boot_bus_width = self.boot_bus_width.tag               
        option_st_obj.option0.timing_interface = self.timing_interface.tag             
        option_st_obj.option0.bus_width = self.bus_width.tag                                           
        option_st_obj.option0.boot_mode = self.boot_mode.tag                    
        option_st_obj.option0.reset_boot_bus_conditions = self.reset_boot_bus_conditions.tag   
        option_st_obj.option0.boot_ack = self.boot_ack.tag                                       
        option_st_obj.option0.boot_config_enable = self.boot_config_enable.tag                                       
        option_st_obj.option1.power_down_time = self.power_down_time.tag              
        option_st_obj.option1.power_polarity = self.power_polarity.tag                                    
        option_st_obj.option1.power_up_time = self.power_up_time.tag                
        option_st_obj.option1.enable_power_cycle = self.enable_power_cycle.tag             
        option_st_obj.option1.instance = self.instance.tag 
        return list(struct.unpack_from(f"<{self.option_st.sizeof()//4}I", self.option_st.build(option_st_obj)))


