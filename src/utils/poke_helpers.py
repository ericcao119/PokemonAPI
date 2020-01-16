"""Helper functions for handling pokemon information"""

from typing import Iterable, Set, Tuple

from src.utils.general import unique_frozen


def add_missing_variants(pokes: Iterable[Tuple[str, str]], variants_dict):
    """Looks for the all the (species, variants) pairs in the set and adds
    any missing variants of the same species. Ensures that each variant will
    only be present once.

    >>> add_missing_variants([("a", "b"), ("b", "c")],
    ... {
    ...     "a" : ["a", "b", "c"],
    ...     "b" : ["c", "d", "e"]
    ... })
    (('a', 'a'), ('a', 'b'), ('a', 'c'), ('b', 'c'), ('b', 'd'), ('b', 'e'))
    """
    jagged = unique_frozen(
        (spec, var) for spec, _ in pokes for var in variants_dict[spec]
    )
    return jagged
