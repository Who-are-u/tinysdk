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
from tinysdk.foo.flash import Flash


class NandFlash(Flash):
    pass


class NandFlashQuad(NandFlash):
    pass


class NandFlashOctal(NandFlash):
    pass

