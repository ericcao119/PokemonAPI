"""This class is for general purpose helper functions targeted for generic python tasks.
This does not mean that they use pure python functions, but instead are things like
list operations that are fairly common."""

import itertools
import dataclasses
import unicodedata
from typing import Generator, List
from itertools import zip_longest

import networkx as nx


def unique(iterable):
    return list(dict.fromkeys(iterable))


def unique_frozen(iterable):
    return tuple(dict.fromkeys(iterable))


def get_components(iterable):
    """Expects a iterable of subiterables (representing subgraph vertices).
    All elements in the subgraph are expected to be hashable vertices. This
    will then return the connected components in the form of a generator
    yeilding sets."""

    def to_graph(l):
        G = nx.Graph()
        for part in l:
            # each sublist is a bunch of nodes
            G.add_nodes_from(part)
            # it also imlies a number of edges:
            G.add_edges_from(to_edges(part))
        return G

    def to_edges(l):
        """ 
        treat `l` as a Graph and returns it's edges 
        to_edges(['a','b','c','d']) -> [(a,b), (b,c),(c,d)]
        """
        it = iter(l)
        last = next(it)

        for current in it:
            yield last, current
            last = current

    G = to_graph(iterable)

    return nx.connected_components(G)


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def grouper_discard_uneven(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip(*args)


def normalize_unicode(string: str) -> str:
    """Removed non-ascii characters from a unicode string. Many characters will be
    converted to their nearest ASCII quivalent."""
    return (
        unicodedata.normalize("NFKD", string).encode("ascii", "ignore").decode("utf-8")
    )


def chunk_list(lst: List, num: int) -> List[List]:
    """Chunks a list in a list of chunks each size num.
    The last chunk may not be divisible by num, but all others will be."""
    return [lst[i : i + num] for i in range(0, len(lst), num)]


def xchunk_list(lst: List, num: int) -> Generator[List, None, None]:
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
