"""Provides some helper functions for defining codecs"""

import enum
import json
from typing import Dict, Any
from dataclasses import asdict, is_dataclass

from bson.codec_options import TypeCodec


def enum_codec_factory(enum_class):
    """This method creates a TypeCodec for generic enums. The Codec produced will
    convert an enum to its string representation for serialization and convert the
    string representation."""
    if issubclass(enum_class, enum.IntEnum):
        raise TypeError("IntEnums cannot be overriden since they subclass from int")

    if not issubclass(enum_class, enum.Enum):
        raise TypeError(f"Type {enum_class} is not a subclass of Enum")

    class EnumCodec(TypeCodec):  # pylint: disable=too-many-ancestors
        """Generic class for generating enum codecs"""

        python_type = enum_class
        bson_type = str

        def transform_python(self, value: enum.Enum):
            return value.name

        def transform_bson(self, value: str):
            return EnumCodec.python_type[value]

    return EnumCodec()


def dataclass_codec_factory(data_class):
    """This method creates a TypeCodec for generic enums. The Codec produced will
    convert an enum to its string representation for serialization and convert the
    string representation."""
    if not is_dataclass(data_class):
        raise TypeError(f"{data_class} is not a valid data_class")

    class DataclassCodec(TypeCodec):  # pylint: disable=too-many-ancestors
        """Generic class for generating dataclass codecs"""

        python_type = data_class
        bson_type = dict

        def transform_python(self, value: data_class):
            return asdict(value)

        def transform_bson(self, value: dict):
            return DataclassCodec.python_type(**value)

    return DataclassCodec()


class JsonEncoderCodec(json.JSONEncoder):
    transforms: Dict[Any, Any] = {}

    def default(self, z):
        if issubclass(type(z), enum.Enum):
            return z.name

        if type(z) in JsonEncoderCodec.transforms:
            return JsonEncoderCodec.transforms[type(z)](z)
        else:
            return super().default(z)
