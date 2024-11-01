# -*- encoding: utf-8 -*-
#@File    :   tinysdkdecorator.py
#@Time    :   2024/07/01 16:51:22
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import logging
import os
import sys
from enum import IntEnum

logger = logging.getLogger("TinysdkFailure")
logger.setLevel(logging.DEBUG)


class TinysdkFailure(list):

    def __init__(self, name: str=""):
        super().__init__()
        self._name = name

    def __str__(self):
        failure = [f"{self._name}"]
        failure.extend([f"{index}: {str(failure)}" for index, failure in enumerate(self)])
        return "\n".join(failure)

    def dump(self):
        logger.warn(self.__str__)

    def log(self, log_file):
        with open(log_file, "wr") as file:
            file.write(self.__str__)
