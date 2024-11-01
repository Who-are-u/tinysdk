# -*- encoding: utf-8 -*-
#@File    :   api_nor.py
#@Time    :   2024/09/04 21:57:32
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   
 


import logging
import os
import sys

from typing import Callable, Iterator, List, Optional, Dict, Any
from tinysdk.foo.media.xspinor import *
from tinysdk.foo.media.lpspi import *
from tinysdk.foo.register import *


class PYBLHOST:
    pass


class APIS():
    """Class for DebugMailboxCommand."""

    STATUS_IS_DATA_MASK = 0x00
    # default delay after sending a command, in seconds
    DELAY_DEFAULT = 0.03

    def __init__(
        self,
        bl: PYBLHOST,
        name: str = "",
        delay: float = DELAY_DEFAULT,
    ):
        """Initialize."""
        self.bl = bl
        self.name = name
        self.delay = delay

    def run(self, params: Optional[List[int]] = None) -> List[Any]:
        """Run DebugMailboxCommand."""
        paramslen = len(params) if params else 0


class OTPAPI_EfuseInit(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="efuse_init")

class OTPAPI_EfuseRead(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="efuse_read")

class OTPAPI_EfuseProgram(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="efuse_program")

class IAPAPI_Init(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_api_init")

class IAPAPI_Deint(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_api_deinit")

class IAPAPI_MemInit(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_mem_init")

class IAPAPI_MemRead(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_mem_read")

class IAPAPI_MemWrite(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_mem_write")

class IAPAPI_MemFill(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_mem_fill")

class IAPAPI_MemErase(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_mem_erase")

class IAPAPI_EraseAll(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_mem_erase_all")

class IAPAPI_MemConfig(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_mem_config")

class IAPAPI_MemFlush(APIS):
    def __init__(self, bl: PYBLHOST):
        super().__init__(bl, name="iap_mem_flush")



