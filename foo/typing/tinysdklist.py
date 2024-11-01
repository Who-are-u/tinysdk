# -*- encoding: utf-8 -*-
#@File    :   hexword_utils.py
#@Time    :   2024/07/05 15:01:02
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import os
import sys,struct

class TinysdkList(list):
    def __init__(self, iterable=[], splite=","):
        super().__init__([])
        self.extend(iterable)
        self.splite = splite

    def __str__(self):
        return f"[{f'{self.splite}'.join([f'{word:#010x}' for word in self])}]"