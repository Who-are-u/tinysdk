# -*- encoding: utf-8 -*-
#@File    :   xspinor.py
#@Time    :   2024/03/28 16:32:07
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import os, sys, time
import struct
import logging
from abc import ABCMeta, abstractproperty, abstractmethod
from dataclasses import dataclass
from construct import Struct, Int64ul, Int32ul, ByteSwapped, BitStruct, BitsInteger
from typing import Callable, Iterator, List, Optional, Dict, Any
from tinysdk.foo.typing import TinysdkEnum


class Flash(metaclass=ABCMeta):
    pass
    