import enum
from dataclasses import dataclass, is_dataclass, asdict
from bson.codec_options import TypeCodec

def EnumCodecFactory(enum_class):
    """This method creates a TypeCodec for generic enums. The Codec produced will
    convert an enum to its string representation for serialization and convert the
    string representation 
    """
    if issubclass(enum_class, enum.IntEnum):
        raise TypeError("IntEnums cannot be overriden since they subclass from int")
    
    if not issubclass(enum_class, enum.Enum):
        raise TypeError(f"Type {enum_class} is not a subclass of Enum")

    class EnumCodec(TypeCodec):
        python_type = enum_class
        bson_type = str

        def transform_python(self, value: enum.Enum):
            return value.name

        def transform_bson(self, value: str):
            return python_type[value]

    return EnumCodec()

def DataclassCodecFactory(data_class):
    """This method creates a TypeCodec for generic enums. The Codec produced will
    convert an enum to its string representation for serialization and convert the
    string representation 
    """
    if not is_dataclass(data_class):
        raise TypeError(f'{data_class} is not a valid data_class')

    class DataclassCodec(TypeCodec):
        python_type = data_class
        bson_type = dict

        def transform_python(self, value: data_class):
            return asdict(value)

        def transform_bson(self, value: dict):
            return python_type(**value)

    return DataclassCodec()