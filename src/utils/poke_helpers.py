"""Helper functions for handling pokemon information"""

from typing import Set, Tuple

from src.utils.general import unique_frozen


def add_missing_variants(pokes: Set[Tuple[str, str]], variants_dict):
    """Looks for the all the (species, variants) pairs in the set and adds
    any missing variants of the same species. Ensures that each variant will
    only be present once."""
    jagged = unique_frozen(
        (spec, var) for spec, _ in pokes for var in variants_dict[spec]
    )
    return jagged
