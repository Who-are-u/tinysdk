# -*- encoding: utf-8 -*-
#@File    :   blhost.py
#@Time    :   2024/07/31 14:50:26
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   
   
from abc import ABCMeta, abstractmethod

class Blhost(metaclass=ABCMeta):

    def __init__(self, probe, name: str=""):
        self._name = name
        self._probe = probe
    
    def write_memory(self, address, size, memory_id: int):
        pass

    def flash_erase_region(self, address, size, memory_id:int):
        pass

    def flash_erase_all(self, address, size, memory_id: int):
        pass

    def efuse_program_once(self, index, value):
        pass

    def efuse_read_once(self, index, value):
        pass


class BlhostAdapter(Blhost):
    
    def __init__(self, probe: blhost):
        super().__init__(probe, name = "Blhost")


class PyBlhostAdapter(Blhost):
    
    def __init__(self, probe: Pyblhost):
        super().__init__(probe, name = "PyBlhost")

    def write_register(self, address, value):
        pass

    def read_register(self, address, value):
        pass
