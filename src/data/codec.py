"""Contains codecs for turning dataclasses into forms representable
in database form"""

from typing import Final

from bson.codec_options import TypeRegistry

from src.data.ability import Ability
from src.data.egg_group_list import EggGroupList
from src.data.pmove import PMove
from src.data.poke_enums import POKE_ENUMS
from src.data.species import Evolution, Species
from src.data.stats import BaseStats, EffortValues
from src.utils.codec_helpers import dataclass_codec_factory, enum_codec_factory

ENUM_CODECS = list(map(enum_codec_factory, POKE_ENUMS))

DATACLASS_CODECS = [
    dataclass_codec_factory(Ability),
    dataclass_codec_factory(PMove),
    dataclass_codec_factory(BaseStats),
    dataclass_codec_factory(EffortValues),
    dataclass_codec_factory(Evolution),
    dataclass_codec_factory(Species),
    dataclass_codec_factory(EggGroupList),
]

CODEC_LIST = ENUM_CODECS + DATACLASS_CODECS

TYPE_REGISTRY: Final[TypeRegistry] = TypeRegistry(type_codecs=CODEC_LIST)
