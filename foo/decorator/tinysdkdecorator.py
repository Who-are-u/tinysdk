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
from tinysdk.foo.exceptions import TinySDKError
from tinysdk.foo.typing.tinysdkfailure import TinysdkFailure



logger = logging.getLogger("TinysdkDecorator")
logger.setLevel(logging.DEBUG)


class TinysdkDecorator:

    def __init__(self, function):
        self._function = function

    def __call__(self, *args, **kwargs):
        logger.info(f"{function.__name__} start")
        logger.info(f"args:{args}")
        ret=self._function(*args, **kwargs)
        logger.info(f"{function.__name__} end")
        return ret
            
    @classmethod
    def log(cls, function):
        def wrapper(*args, **kwargs):
            logger.info(f"{function.__name__} start")
            logger.info(f"args:{args}")
            ret=function(*args, **kwargs)
            logger.info(f"{function.__name__} end")
            return ret
        return wrapper

    @staticmethod
    def retry(count):
        def decorator(function):
            def wrapper(*args, **kwargs):
                logger.info(f"{function.__name__} start")
                logger.info(f"args:{args}")
                failure = TinysdkFailure(f"{function.__name__}")
                for cnt in range(count):
                    logger.info(f"Retry({cnt}).")
                    try:
                        ret=function(*args, **kwargs)
                    except:
                        failure.append(f"Retry({cnt}) failed.")
                    finally:
                        if len(failure) > 0:
                            raise TinySDKError(f"{str(failure)}")
                    logger.info(f"{function.__name__} end")
                return ret
            return wrapper
        return decorator