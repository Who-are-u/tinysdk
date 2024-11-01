# -*- encoding: utf-8 -*-
#@File    :   elftosb.py
#@Time    :   2024/09/04 21:42:57
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   



import logging
import os,sys
import json, re
# sys.path.append(os.path.join(os.path.dirname(__file__),"../"))
# sys.path.append(os.path.join(os.path.dirname(__file__),"../../"))
# sys.path.append(os.path.join(os.path.dirname(__file__),"../../../"))

from mcutk.util import run_command
from tinysdk.foo.exceptions import *
from tinysdk.foo.utils import RKTH


class Elftosb():

    exe = "C:/Users/nxf91386/elftosb_v5.2.7.21.exe"
    @classmethod
    def to_sign(self, family="nx32nx", config=None):
        command = [
            f'"{Elftosb.exe}"',
            f'-V ',
            f'-f {family}',
            f'-J {config}'
        ] 
        bl_cmd = ' '.join(command)
        logging.info('Running blhost command...\n%s'%bl_cmd) 
        rc_output = run_command(cmd=bl_cmd,
                                shell=True,
                                stdout='capture',
                                timeout=15*60)
        output = rc_output[1]
        logging.info(output)

        matches = re.findall(r'RoTKTH: (.*)', output)
        if matches != None:
            RoTKTH = matches[0]
        else:
            raise TinySDKValueError("Not find RoTKTH.")

        matches = re.findall(r'Writing output image \((.*?)\)', output)
        if matches != None:
            output_bin_file = matches[0]
        else:
            raise TinySDKValueError("Not find output file.")

        logging.info(RoTKTH)
        logging.info(output_bin_file)
        
        # RoTKTH_bytes = bytes.fromhex(RoTKTH)
        # rkth = [int.from_bytes(RoTKTH_bytes[n*4: n*4 + 4], "little") for n in range(len(RoTKTH_bytes)//4)]

        return RKTH.fromhex(RoTKTH), output_bin_file
       
# if __name__ == '__main__':
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format='\n%(asctime)s - %(filename)s - %(levelname)s [Line %(lineno)d]\n%(message)s'
#     )
#     config = "Z:/rom_auto/rom_testcaselib/imxrt700_b0_pre/test_config/boot_image_config.json"
#     Elftosb.to_sign(config = config)