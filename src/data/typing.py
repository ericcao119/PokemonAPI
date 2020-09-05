"""Some short hand for typing information about identifiers"""
from typing import Tuple

ItemId = str
MoveId = str
SpeciesId = str
VariantId = str

PokeId = Tuple[SpeciesId, VariantId]
