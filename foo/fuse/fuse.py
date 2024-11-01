# -*- encoding: utf-8 -*-
#@File    :   fuse.py
#@Time    :   2024/09/04 21:40:36
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   
 


import os
import sys,struct,logging
from construct import Struct, Int64ul, Int32ul, ByteSwapped, BitStruct, BitsInteger
from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional
from tinysdk.foo.media.xspinor import *
from tinysdk.foo.typing import TinysdkEnum
from tinysdk.foo.exceptions import *
from typing_extensions import Self
from rom_utils.imggen.sbloader.sbloader3v1 import (
    KeyWrapId, SB3xCmdExecute, SB3xCmdFillMemory, SB3xCmdLoad, SB3xFile, SB3xImageType, SB3xCmdConfigureMemory, SB3xCmdProgramFuses
)
from tinysdk.foo.typing.tinysdkfailure import TinysdkFailure
from tinysdk.foo.exceptions import TinySDKError
from tinysdk.foo.register.register import *
from abc import ABCMeta, abstractmethod
from rom_features.trust_provisioning.trust_provisioning import OEM_PROV_FW,OEM_CKDFK
from rom_utils.keys_certs import AHABKeysCerts



class FuseSettings(dict):
    """ FuseSettings class"""

    def __init__(self, label:str ="")-> None:
        super().__init__()
        self._label = label 

    def __str__(self)->str:
        return self._label + "\n" + "\n".join([f"{key}: {value : #010x}" for key, value in self.items()])
         
    def __call__(self, blhost):
        logging.info(f"\n{self._label:}\n")
        failure = TinysdkFailure()
        for key, value in self.items():
            try:
                blhost.efuse_program_once(key, value)
            except:
                failure.append(f"Failed to program {key} : {value : #010x}")
            else:
                logging.info(f"Success to program {key} : {value : #010x}")
                
        logging.info(str(failure))
        assert len(failure) == 0

    def __add__(self, other):
        """Override operator '+', allow two object of Self +, such a + b.
        
        """
        new_one = self.__class__()    
        for key1, val1 in self.items():
            if key1 in other.keys():
                new_one[key1] = val1 | other[key1]
            else:
                new_one[key1] = val1

        for key2, val2 in other.items():
            if key2 not in self.keys():
                new_one[key2] = val2

        return new_one

    def update(self, other:dict):
        """Override method update. support {key, int} and {key, list}, list parse
        
        """
        for key, value in other.items():
            if isinstance(value, int):
                super().update({key: value})
            elif isinstance(value, list):
                for sub_key, sub_value in enumerate(value):
                    super().update({key + sub_key: sub_value})
            else:
                logging.error(
                    f'TypeError for the element in <fuse_settings>! Got {type(value)}, '
                    f'but expected {int} or {list}!\n'
                )
                raise TypeError

    def to_sb3(self)-> list:
        """ Covert all fuse settings into List[SB3xCmdProgramFuses]

        Return Value: list of sb3 SB3xCmdProgramFuses.
        """
        sb3_commands = []
        for key, value in self.items():
            sb3_commands.append(SB3xCmdProgramFuses(key, [value]))
        return sb3_commands

    @classmethod
    def from_list(cls, key_start: int, val_list: list, label:str="")->Self:
        if not isinstance(val_list, list):
            raise TinySDKError(f"The val_list must be type of list, but it is {type(val_list)}.")
        
        fuse_settings = cls(label)
        fuse_settings.update({key_start: val_list})
        return fuse_settings



class FuseSettingsMap(FuseSettings):
    """ Fuse Map class"""

    def __init__(self, other:dict):
        super().__init__()
        self.update(other)

    def __str__(self)->str:
        return self._label + "\n" + "\n".join([f"{key}: {value : #013x}" for key, value in self.items()])
    
    @classmethod
    def from_val(cls, val_file):
        if not os.path.exists(val_file):
            raise TinySDKValueError(f"{val_file} does not exists")

        fuse_settings = {}
        with open(val_file, "r") as file:
            fuse_lines = file.readlines()
            for index, fuse_line in enumerate(fuse_lines):
                fuse_word = int(fuse_line[0:-1],16)
                fuse_settings.update({index: fuse_word})
        return cls(fuse_settings)

    @classmethod
    def new(cls):
        return cls(FuseSettings.from_list(0, [0 for n in range(512)]))

    @classmethod
    def to_val(cls, val_file, other: Self):
        fuse_lines = [f"{fuse_word: 013x}\n"[2:] for fuse_word in other.values()]
        with open(val_file, "w") as file:
            file.writelines(fuse_lines)
        return val_file

class FuseInterface(metaclass=ABCMeta):
    def __init__(self, name: str="") -> None:
        self.name = name

    def init(self):
        pass

    def deinit(self):
        pass

    @abstractmethod
    def read(self, fuse_index: int):
        pass

    @abstractmethod
    def write(self, fuse_settings: dict):
        pass

class InterfaceBlhostEfuse(FuseInterface):
    def __init__(self, blhost) -> None:
        super().__init__("blhost efuse")
        self.blhost = blhost

    def read(self, fuse_index: int):
        return self.blhost.efuse_read_once(fuse_index)

    def write(self, fuse_settings: dict):
        for fuse_index, value in fuse_settings.items():
            self.blhost.efuse_program_once(fuse_index,value)

class InterfacePyblhostEfuse(FuseInterface):
    def __init__(self, pyblhost) -> None:
        super().__init__("pyblhost efuse")
        self.pyblhost = pyblhost

    def init(self):
        self.pyblhost.rom_api_otp_efuse_init()

    def deinit(self):
        self.pyblhost.rom_api_otp_efuse_deinit()

    def read(self, fuse_index: int):
        return self.pyblhost.rom_api_otp_efuse_read(fuse_index)

    def write(self, fuse_settings: dict):
        for fuse_index, value in fuse_settings.items():
            self.pyblhost.rom_api_otp_efuse_program(fuse_index,value)
    
class InterfacePyblhostShadowRegister(FuseInterface):
    def __init__(self, pyblhost, shadow_register_base: int) -> None:
        super().__init__("pyblhost shadow register")
        self.registercontext =  RegisterContext(InterfacePyblhost(pyblhost))
        self.shadow_register_base = shadow_register_base

    def read(self, fuse_index: int):
        return self.registercontext.read(Register(self.shadow_register_base + fuse_index*4))


    def write(self, fuse_settings: dict):
        for fuse_index, value in fuse_settings.items():
            self.registercontext.write(Register(self.shadow_register_base + fuse_index*4), value)
    
class InterfaceBlhostSB3Efuse(FuseInterface):
    def __init__(self, blhost, keys_certs):
        super().__init__("sb3 efuse")
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

    def read(self, fuse_index: int):
        raise TinySDKError("Do not support.")

    def write(self, fuse_settings: dict):
        sb_command_list = []
        for fuse_index, value in fuse_settings.items():
            sb_command_list.append(SB3xCmdProgramFuses(fuse_index, [value]))

        return self.execute(sb_command_list)

class FuseContext():
    def __init__(self, fuse_interface: FuseInterface) -> None:
        self.fuse_interface = fuse_interface

    def set_interface(self, fuse_interface: FuseInterface) -> None:
        self.fuse_interface = fuse_interface

    def init(self):
        self.fuse_interface.init()

    def deinit(self):
        self.fuse_interface.deinit()

    def read(self, fuse_index: int):
        return self.fuse_interface.read(fuse_index)

    def write(self, fuse_settings: dict):
        self.fuse_interface.write(fuse_settings)

