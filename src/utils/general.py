import dataclasses
from typing import List


"""This class is for general purpose helper functions targeted for generic python tasks"""


def chunk_list(lst: List, n: int) -> List[List]:
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def xchunk_list(lst: List, n: int) -> List[List]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def add_slots(cls):
    # Need to create a new class, since we can't set __slots__
    #  after a class has been created.

    # Make sure __slots__ isn't already set.
    if '__slots__' in cls.__dict__:
        raise TypeError(f'{cls.__name__} already specifies __slots__')

    # Create a new dict for our new class.
    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in dataclasses.fields(cls))
    cls_dict['__slots__'] = field_names
    for field_name in field_names:
        # Remove our attributes, if present. They'll still be
        #  available in _MARKER.
        cls_dict.pop(field_name, None)
    # Remove __dict__ itself.
    cls_dict.pop('__dict__', None)
    # And finally create the class.
    qualname = getattr(cls, '__qualname__', None)
    cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    if qualname is not None:
        cls.__qualname__ = qualname
    return cls


def separate_conjuctive(a: str):
    r""" DO NOT USE THIS FUNCTION IF YOU ARE UNSURE OF THE FORM OF THE INPUT.
    This is a very specific function for capturing strings of the form:
    'a and b and c ...' or
    'a, b, c, ..., and d'

    It returns a list of the form [a, b, c, d, ...]
    """
    # TODO: Make this more generalizable

    if ',' in a:
        return [i.replace(' and ', '').strip() for i in a.split(',')]
    elif ' and ' in a:
        return [i.strip() for i in a.split(' and ')]
    else:
        return [a]
