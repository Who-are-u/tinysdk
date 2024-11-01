# -*- encoding: utf-8 -*-
#@File    :   bootimage.py
#@Time    :   2024/09/04 21:40:58
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   
   


import logging
import os
import sys

from tinysdk.foo.image import CortexMImage
from tinysdk.foo.fuse import *
from abc import ABCMeta, abstractproperty, abstractmethod



class BootImage():

    def __init__(self, raw_image: CortexMImage, bin_file: str, fuse_settings: FuseSettings=FuseSettings()):
        self._raw_image = raw_image
        self._bin_file = bin_file
        self._fuse_settings = fuse_settings

    @property
    def raw_image(self):
        return self._raw_image

    @property
    def bin_file(self):
        return self._bin_file

    @bin_file.setter
    def bin_file(self, file):
        self._bin_file = file

    @property
    def fuse_settings(self):
        return self._fuse_settings

    @fuse_settings.setter
    def fuse_settings(self, _fuse_settings):
        self._fuse_settings = _fuse_settings

    def __str__(self):
        return "\n".join([str(self.raw_image), str(self.bin_file), str(self.fuse_settings)])


