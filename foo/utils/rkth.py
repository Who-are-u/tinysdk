# -*- encoding: utf-8 -*-
#@File    :   iped_utils.py
#@Time    :   2024/05/27 15:12:17
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   RKTH.



import os
import sys,struct
from construct import Struct, Int64ul, Int32ul, ByteSwapped, BitStruct, BitsInteger
from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional
from typing_extensions import Self
sys.path.append(os.path.join(os.path.dirname(__file__),"../"))
sys.path.append(os.path.join(os.path.dirname(__file__),"../../"))
sys.path.append(os.path.join(os.path.dirname(__file__),"../../../"))
from tinysdk.foo.fuse import FuseSettings


class RKTH(list):

    def __init__(self, rkth_list:list)-> None:
        self.extend(rkth_list)

    def fuse_settings(self, fuse_offset: int, label="RKTH"):
        return FuseSettings.from_list(fuse_offset, self, label=label)

    @classmethod
    def hex(cls, rkth_list: Self)->str:
        return "".join([bytes.hex((int.to_bytes(x, 4, "little"))) for x in rkth_list])
        
    @classmethod
    def fromhex(cls, rkth_hex: str)->Self:
        rkth_words= struct.unpack(f"<{len(bytes.fromhex(rkth_hex))//4}I", bytes.fromhex(rkth_hex))
        return cls(list(rkth_words))
    

if __name__ == '__main__':

    rkth = RKTH.fromhex("1122334455667788")
    print(RKTH.hex(rkth))
    print(rkth.fuse_settings(80))

    