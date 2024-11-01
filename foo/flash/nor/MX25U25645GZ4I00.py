# -*- encoding: utf-8 -*-
#@File    :   xspinor.py
#@Time    :   2024/03/28 16:32:07
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import os,sys,logging,time,sys
from abc import ABCMeta, abstractproperty, abstractmethod
from construct import Struct, Int64ul, Int32ul, ByteSwapped, BitStruct, BitsInteger
from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional, Dict, Any
from tinysdk.foo.flash import NorFlashQuad, NorFlashOctal


class MX25U25645GZ4I00(NorFlashQuad):
    def __str__(self):
        return "MX25U25645GZ4I00"






