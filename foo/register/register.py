# -*- encoding: utf-8 -*-
#@File    :   register.py
#@Time    :   2024/09/04 21:42:18
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   
   


import logging
import os,sys
import time
from abc import ABCMeta, abstractmethod
from tinysdk.foo.typing import TinysdkEnum
from tinysdk.foo.exceptions import TinySDKIOError

from rom_utils.debugger.debugger import Debugger


class Register():
    """Register class."""

    def __init__(self, address: int, name: str="", fields: TinysdkEnum = None):
        self._name = name
        self._address = address
        self._fields = fields

    def __str__(self):
        return self._name


class RegisterInterface(metaclass=ABCMeta):
    def __init__(self, name: str="") -> None:
        self.name = name

    @abstractmethod
    def read(self, register: Register):
        pass

    @abstractmethod
    def write(self, register: Register, value: int):
        pass


class InterfaceJlink(RegisterInterface):
    def __init__(self, jlink: Debugger) -> None:
        super().__init__("jlink")
        self.jlink = jlink

    def read(self, register: Register):
        try:
            read_value = self.jlink.read32(register._address)
        except Exception as e:
            assert False, e
        else:
            return 0, [read_value]

    def write(self, register: Register, value: int):
        return self.jlink.write32(register._address, value)


class InterfacePyblhost(RegisterInterface):
    def __init__(self, pyblhost) -> None:
        super().__init__("pyblhost")
        self.pyblhost = pyblhost

    def read(self, register: Register):
        return self.pyblhost.read_reg32(register._address)

    def write(self, register: Register, value: int):
        return self.pyblhost.write_reg32(register._address, value)


class RegisterContext():
    def __init__(self, register_interface: RegisterInterface) -> None:
        self.register_interface = register_interface

    def set_interface(self, register_interface: RegisterInterface) -> None:
        self.register_interface = register_interface

    def read(self, register: Register):
        return self.register_interface.read(register)

    def write(self, register: Register, value: int):
        return self.register_interface.write(register, value)

