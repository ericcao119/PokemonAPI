from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

from src.data.poke_enums import PType, LevelingRate, EggGroup, Color, Shape, Habitat, EvolutionType
from src.data.stats import BaseStats, EffortValues
from src.data.ability import Ability
from src.utils.general import add_slots

PMoveName = str
ItemName = str
SpeciesName = str
VariantName = str


@add_slots
@dataclass
class Evolution:
    """Requirements"""
    evolution_type: EvolutionType = EvolutionType.INVALID
    item_reqr: ItemName = ''
    numeric_reqr: int = -1
    species_reqr: SpeciesName = ''
    location_reqr: str = ''

    evolution_form: SpeciesName = ''
    variant_form: VariantName = ''

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)


@add_slots
@dataclass
class Species:
    species_name: SpeciesName = ''
    variant_num: int = -1
    variant_name: VariantName = ''

    types: List[PType] = field(default_factory=lambda: [
                               PType.INVALID, PType.INVALID])
    base_stats: BaseStats = BaseStats(0, 0, 0, 0, 0, 0)
    gender_rate: int = 127
    leveling_rate: LevelingRate = LevelingRate.INVALID
    base_exp_yield: int = -1
    effort_points: EffortValues = EffortValues(0, 0, 0, 0, 0, 0)

    # Bounded int in [0, 255]
    catch_rate: int = -1

    # Bounded int in [0, 255]
    base_friendship: int = -1

    # Learn by level-up
    learned_moves: List[PMoveName] = field(default_factory=lambda: [])

    egg_groups: List[EggGroup] = field(
        default_factory=lambda: [EggGroup.INVALID])

    # Hatch Time
    steps_to_hatch_lower: int = -1
    steps_to_hatch_upper: int = -1

    # Height in meters
    height: float = -1.0
    weight: float = -1.0
    color: Color = Color.INVALID
    shape: Shape = Shape.INVALID
    kind: str = ''
    flavor_text: str = ''

    abilities: List[Ability] = field(default_factory=lambda: [])
    hidden_abilities: List[Ability] = field(default_factory=lambda: [])
    egg_moves: List[PMoveName] = field(default_factory=lambda: [])
    tm_moves: List[PMoveName] = field(default_factory=lambda: [])

    habitat: Habitat = Habitat.INVALID

    regional_dex_nums: List[int] = field(default_factory=lambda: [])

    # The chances of holding the item are 50%, 5% and 1% respectively.
    # If all three are the same item, then the chance of holding it is 100% instead.

    wild_item_common: ItemName = ''
    wild_item_uncommmon: ItemName = ''
    wild_item_rare: ItemName = ''

    BattlerPlayerY: int = 0
    BattlerEnemyY: int = 0
    BattlerAltitude: int = 0

    evolutions: List[Evolution] = field(default_factory=lambda: [])

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)
