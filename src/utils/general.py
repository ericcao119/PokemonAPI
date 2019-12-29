"""This class is for general purpose helper functions targeted for generic python tasks"""

import dataclasses
from typing import List


def chunk_list(lst: List, num: int) -> List[List]:
    """Chunks a list in a list of chunks each size num.
    The last chunk may not be divisible by num, but all others will be."""
    return [lst[i : i + num] for i in range(0, len(lst), num)]


def xchunk_list(lst: List, num: int) -> List[List]:
    """Chunks a list in a list of chunks each size num.
    The last chunk may not be divisible by num, but all others will be."""
    for i in range(0, len(lst), num):
        yield lst[i : i + num]


def add_slots(cls):
    """Decorator for adding slots to a dataclass"""
    # Need to create a new class, since we can't set __slots__
    #  after a class has been created.

    # Make sure __slots__ isn't already set.
    if "__slots__" in cls.__dict__:
        raise TypeError(f"{cls.__name__} already specifies __slots__")

    # Create a new dict for our new class.
    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in dataclasses.fields(cls))
    cls_dict["__slots__"] = field_names
    for field_name in field_names:
        # Remove our attributes, if present. They'll still be
        #  available in _MARKER.
        cls_dict.pop(field_name, None)
    # Remove __dict__ itself.
    cls_dict.pop("__dict__", None)
    # And finally create the class.
    qualname = getattr(cls, "__qualname__", None)
    cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    if qualname is not None:
        cls.__qualname__ = qualname
    return cls
