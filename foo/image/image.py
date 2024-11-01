# -*- encoding: utf-8 -*-
#@File    :   image.py
#@Time    :   2024/04/16 17:54:12
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   

import os
import sys
from abc import ABCMeta, abstractproperty, abstractmethod
import json,logging
from typing import Callable, Iterator, List, Optional, Dict, Any
from dataclasses import dataclass


class ImageDescriptor():
    """ Raw image descriptor class.

    """
    def __init__(self):
        self._images_array = dict()

    def get(self, image_name: str=None):
        return self._images_array[image_name]

    def set(self, image_name:str=None, file_path:str =None)->None : 
        self._images_array[image_name] = file_path

    def info(self)->None : 
        for key, image in self._images_array.items():
            print(str(image))


class Image(metaclass=ABCMeta):
    """ Interfaces of images. i.e., core_id,load_address and entry_address

    """
    def __init__(self, bin_file: str, core_id: int, load_address: int, entry_address: int)-> None:
        """Load raw images.

        :param bin_file: binary file.
        :param core_id: core id.
        :param load_address: load address.
        :param entry_address: entry address.
        """
        if not os.path.exists(bin_file):
            raise ValueError(f'{bin_file} does not exist')

        self._attributes={}
        self._attributes["core_id"] = core_id
        self._attributes["load_address"] = load_address
        self._attributes["entry_address"] = entry_address
        self._attributes["bin_file"] = bin_file

    @property
    def bin_file(self):
        return self._attributes["bin_file"]

    @property
    def core_id(self):
        return self._attributes["core_id"]
    
    @property
    def load_address(self):
        return self._attributes["load_address"]

    @property
    def entry_address(self):
        return  self._attributes["entry_address"]

    @abstractmethod
    def __str__(self):
        pass  

    @classmethod
    def load(cls: Any, base_dir: str) -> Dict[str, Any]:
        """Load raw images.

        :param base_dir: direction of raw images.
        :return: Return cls instance Dict.
        """
        if not os.path.exists(base_dir):
            logging.info(f"{base_dir} does not exist")
            return dict()
        
        files = [os.path.join(base_dir, file) for file in os.listdir(base_dir)]
        raw_images = ImageDescriptor()
        for file in files:
            if os.path.isfile(file):
                lable = os.path.basename(file)
                load_address = lable.split("_")[-1][0:-4]
                raw_image = cls(file.replace("\\", "/"), 1, int(load_address,16), int(load_address,16))
                raw_images.set(lable[0:-4], raw_image)
            
        return raw_images


class CortexMImage(Image):
    """ MCU raw image class.

    """
    def __str__(self):
        info =(
            f"core_id: {self.core_id};" + 
            f"bin_file: {self.bin_file};"  + 
            f"load_address: {self.load_address:#010x};" + 
            f"entry_address: {self.entry_address:#010x};"
        )
        return info
        

    