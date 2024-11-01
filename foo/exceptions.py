# -*- encoding: utf-8 -*-
#@File    :   exceptions.py
#@Time    :   2024/09/04 21:42:37
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


"""Base for TinySDK exceptions."""
from typing import Optional

#######################################################################
# # Secure Provisioning SDK Exceptions
#######################################################################


class TinySDKError(Exception):
    """Secure Provisioning SDK Base Exception."""

    fmt = "TinySDK: {description}"

    def __init__(self, desc: Optional[str] = None) -> None:
        """Initialize the base TinySDK Exception."""
        super().__init__()
        self.description = desc

    def __str__(self) -> str:
        return self.fmt.format(description=self.description or "Unknown Error")


class TinySDKKeyError(TinySDKError, KeyError):
    """TinySDK standard key error."""


class TinySDKValueError(TinySDKError, ValueError):
    """TinySDK standard value error."""


class TinySDKTypeError(TinySDKError, TypeError):
    """TinySDK standard type error."""


class TinySDKIOError(TinySDKError, IOError):
    """TinySDK standard IO error."""


class TinySDKNotImplementedError(TinySDKError, NotImplementedError):
    """TinySDK standard not implemented error."""


class TinySDKLengthError(TinySDKError, ValueError):
    """TinySDK parsing error of any AHAB containers.

    Input/output data must be of at least container declared length bytes long.
    """


class TinySDKOverlapError(TinySDKError, ValueError):
    """Data overlap error."""


class TinySDKAlignmentError(TinySDKError, ValueError):
    """Data improperly aligned."""


class TinySDKParsingError(TinySDKError):
    """Cannot parse binary data."""


class TinySDKCorruptedException(TinySDKError):
    """Corrupted Exception."""


class TinySDKUnsupportedOperation(TinySDKError):
    """TinySDK unsupported operation error."""


class TinySDKSyntaxError(SyntaxError, TinySDKError):
    """TinySDK syntax error."""


class TinySDKFileNotFoundError(FileNotFoundError, TinySDKError):
    """TinySDK file not found error."""


class TinySDKAttributeError(TinySDKError, AttributeError):
    """TinySDK standard attribute error."""


class TinySDKConnectionError(TinySDKError, ConnectionError):
    """TinySDK standard connection error."""


class TinySDKIndexError(TinySDKError, IndexError):
    """TinySDK standard index error."""
