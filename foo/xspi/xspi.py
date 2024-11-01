# -*- encoding: utf-8 -*-
#@File    :   xspinor.py
#@Time    :   2024/03/28 16:32:07
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


import os,sys,struct
import logging
from tinysdk.foo.typing import TinysdkEnum

class EnumXspiInstance(TinysdkEnum):
    xSPI0 = (0, "xSPI0", "xSPI0")
    xSPI1 = (1, "xSPI1", "xSPI1")
    xSPI2 = (2, "xSPI2", "xSPI2")
    xSPI3 = (3, "xSPI3", "xSPI3")  

