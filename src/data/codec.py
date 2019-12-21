from bson.codec_options import TypeRegistry, CodecOptions

from src.utils.codec_helpers import EnumCodecFactory
from src.utils.codec_helpers import DataclassCodecFactory

from src.data.poke_enums import PType, LevelingRate, EggGroup
from src.data.poke_enums import Color, Shape, Habitat, EvolutionType

from src.data.ability import Ability
from src.data.egg_group_list import EggGroupList

from src.data.pmove import PMove
from src.data.stats import BaseStats, EffortValues
from src.data.species import Evolution, Species

PTypeCodec = EnumCodecFactory(PType)
GrowthRateCodec = EnumCodecFactory(LevelingRate)
EggGroupCodec = EnumCodecFactory(EggGroup)
ColorCodec = EnumCodecFactory(Color)
ShapeCodec = EnumCodecFactory(Shape)
HabitatCodec = EnumCodecFactory(Habitat)
EvolutionTypeCodec = EnumCodecFactory(EvolutionType)

AbilityCodec = DataclassCodecFactory(Ability)
PMoveCodec = DataclassCodecFactory(PMove)
BaseStatsCodec = DataclassCodecFactory(BaseStats)
EffortValuesCodec = DataclassCodecFactory(EffortValues)
EvolutionCodec = DataclassCodecFactory(Evolution)
SpeciesCodec = DataclassCodecFactory(Species)
EggGroupListCodec = DataclassCodecFactory(EggGroupList)

codec_list = [
    PTypeCodec,
    GrowthRateCodec,
    EggGroupCodec,
    ColorCodec,
    ShapeCodec,
    HabitatCodec,
    EvolutionTypeCodec,
    PMoveCodec,
    BaseStatsCodec,
    EffortValuesCodec,
    EvolutionCodec,
    SpeciesCodec,
    EggGroupListCodec,
    AbilityCodec,
]

TYPE_REGISTRY = TypeRegistry(type_codecs=codec_list)