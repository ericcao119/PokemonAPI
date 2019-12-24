from typing import Final
from bson.codec_options import TypeRegistry

from src.utils.codec_helpers import EnumCodecFactory
from src.utils.codec_helpers import DataclassCodecFactory

from src.data.poke_enums import PokeEnums

from src.data.ability import Ability
from src.data.egg_group_list import EggGroupList

from src.data.pmove import PMove
from src.data.stats import BaseStats, EffortValues
from src.data.species import Evolution, Species

EnumCodecs = list(map(EnumCodecFactory, PokeEnums))

AbilityCodec = DataclassCodecFactory(Ability)
PMoveCodec = DataclassCodecFactory(PMove)
BaseStatsCodec = DataclassCodecFactory(BaseStats)
EffortValuesCodec = DataclassCodecFactory(EffortValues)
EvolutionCodec = DataclassCodecFactory(Evolution)
SpeciesCodec = DataclassCodecFactory(Species)
EggGroupListCodec = DataclassCodecFactory(EggGroupList)

codec_list = EnumCodecs + [
    PMoveCodec,
    BaseStatsCodec,
    EffortValuesCodec,
    EvolutionCodec,
    SpeciesCodec,
    EggGroupListCodec,
    AbilityCodec,
]

TYPE_REGISTRY: Final[TypeRegistry] = TypeRegistry(type_codecs=codec_list)
