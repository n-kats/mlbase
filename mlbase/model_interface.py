"""
モデルの入出力のインターフェイスを扱う
"""

from sys import stdout
from enum import Flag, auto
from collections import OrderedDict
from typing import NamedTuple, Any, Dict

import tensorflow as tf


class Role(Flag):
    INPUT = auto()
    TRAIN_ONLY = auto()
    HAS_DEFAULT = auto()
    GROUND_TRUTH = auto()


class _InputVariable(NamedTuple):
    name: str
    dtype: Any
    shape: list
    description: str
    role: Role


class ModelInterface:
    """
    >>> model_if = ModelInterface("FooModeInput")
    >>> model_if.add("input_image", tf.float32, [None, None, None, 3], "image", Role.INPUT)
    >>> placeholder = model_if.get("input_image")
    """

    def __init__(self, description):
        self.__description = description
        self.__input_variables: Dict[str, _InputVariable] = OrderedDict()
        self.__input_ops = OrderedDict()

    def add(self, name: str, dtype, shape, description: str, role: Role):
        assert name not in self.__input_variables, Exception("名前が重複しています")
        self.__input_variables[name] = _InputVariable(
            name=name,
            dtype=dtype,
            shape=shape,
            description=description,
            role=role)
        self.__input_ops[name] = tf.placeholder(dtype, shape, name)

    def get(self, name):
        assert name in self.__input_ops
        return self.__input_ops[name]

    def show(self, writer=stdout):
        for var in self.__input_variables:
            print(var, file=writer)

    def feed_dict(self, name_to_val):
        """
        feed_dictを作成する。
        Args:
            name_to_val(dict): 変数名に対し、そこに適用する値を持つ辞書
        """
        result = {}
        for key, val in name_to_val.items():
            result[self.get(key)] = val
        return result
