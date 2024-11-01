#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2023 NXP
#
# SPDX-License-Identifier: BSD-3-Clause
# -*- encoding: utf-8 -*-
#@File    :   tinysdkenum.py
#@Time    :   2024/03/28 16:32:39
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


"""Custom enum extension."""
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional, Union, Any

from typing_extensions import Self



@dataclass(frozen=True)
class TinysdkEnumMember:
    """TinySDK Enum member."""

    tag: int
    label: str
    # description: Optional[str] = None
    description: Any = None


class TinysdkEnum(TinysdkEnumMember, Enum):
    """TinySDK Enum type."""

    def __eq__(self, __value: object) -> bool:
        return self.tag == __value or self.label == __value

    def __hash__(self) -> int:
        return hash((self.tag, self.label, self.description))

    def __str__(self):
        return self.label

    @classmethod
    def members(cls) -> List[Self]:
        """Get list of labels of all enum members.

        :return: List of all labels
        """
        return [value for value in cls.__members__.values()]
    
    @classmethod
    def labels(cls) -> List[str]:
        """Get list of labels of all enum members.

        :return: List of all labels
        """
        return [value.label for value in cls.__members__.values()]

    @classmethod
    def tags(cls) -> List[int]:
        """Get list of tags of all enum members.

        :return: List of all tags
        """
        return [value.tag for value in cls.__members__.values()]

    @classmethod
    def contains(cls, obj: Union[int, str]) -> bool:
        """Check if given member with given tag/label exists in enum.

        :param obj: Label or tag of enum
        :return: True if exists False otherwise
        """
        if not isinstance(obj, (int, str)):
            raise ValueError("Object must be either string or integer")
        try:
            cls.from_attr(obj)
            return True
        except ValueError:
            return False

    @classmethod
    def get_tag(cls, label: str) -> int:
        """Get tag of enum member with given label.

        :param label: Label to be used for searching
        :return: Tag of found enum member
        """
        value = cls.from_label(label)
        return value.tag

    @classmethod
    def get_label(cls, tag: int) -> str:
        """Get label of enum member with given tag.

        :param tag: Tag to be used for searching
        :return: Label of found enum member
        """
        value = cls.from_tag(tag)
        return value.label

    @classmethod
    # def get_description(cls, tag: int, default: Optional[str] = None) -> Optional[str]:
    def get_description(cls, tag: int, default: Any = None) -> Any:
        """Get description of enum member with given tag.

        :param tag: Tag to be used for searching
        :param default: Default value if member contains no description
        :return: Description of found enum member
        """
        value = cls.from_tag(tag)
        return value.description or default

    @classmethod
    def from_attr(cls, attribute: Union[int, str]) -> Self:
        """Get enum member with given tag/label attribute.

        :param attribute: Attribute value of enum member
        :return: Found enum member
        """
        from_tag: Callable = cls.from_tag
        from_label: Callable = cls.from_label
        from_method: Callable = from_tag if isinstance(attribute, int) else from_label
        return from_method(attribute)

    @classmethod
    def from_tag(cls, tag: int) -> Self:
        """Get enum member with given tag.

        :param tag: Tag to be used for searching
        :raises TinySDKKeyError: If enum with given label is not found
        :return: Found enum member
        """
        for item in cls.__members__.values():
            if item.tag == tag:
                return item
        raise ValueError(f"There is no {cls.__name__} item in with tag {tag} defined")

    @classmethod
    def from_label(cls, label: str) -> Self:
        """Get enum member with given label.

        :param label: Label to be used for searching
        :raises TinySDKKeyError: If enum with given label is not found
        :return: Found enum member
        """
        for item in cls.__members__.values():
            if item.label.upper() == label.upper():
                return item
        raise ValueError(f"There is no {cls.__name__} item with label {label} defined")


