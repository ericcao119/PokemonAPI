"""Dataclasses for describing a pokemon variant"""

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

from src.data.ability import Ability
from src.data.poke_enums import EvolutionType  # Habitat,
from src.data.poke_enums import Color, EggGroup, LevelingRate, PType, Shape
from src.data.stats import BaseStats, EffortValues
from src.data.typing import ItemId, MoveId, SpeciesId, VariantId
from src.utils.general import add_slots


@add_slots
@dataclass
class Evolution:
    """Requirements for evolution"""

    evolution_type: EvolutionType = EvolutionType.INVALID
    item_reqr: ItemId = ""
    numeric_reqr: int = -1
    species_reqr: SpeciesId = ""
    location_reqr: str = ""

    evolution_form: SpeciesId = ""
    variant_form: VariantId = ""

    def _asdict(self) -> Dict:
        return asdict(self)


@add_slots
@dataclass
class DexEntryComponent:
    """Dex information"""

    # Height in meters
    national_dex_num: int = -1
    types: List[PType] = field(default_factory=lambda: [PType.INVALID, PType.INVALID])
    height: float = -1.0
    weight: float = -1.0
    color: Color = Color.INVALID
    shape: Shape = Shape.INVALID
    kind: str = ""
    flavor_text: str = ""

    abilities: List[Ability] = field(default_factory=lambda: [])
    hidden_abilities: List[Ability] = field(default_factory=lambda: [])
    regional_dex_nums: List[int] = field(default_factory=lambda: [])

    def _asdict(self) -> Dict:
        return asdict(self)


@add_slots
@dataclass
class TrainingComponent:
    """Contains all variant information about training with/against a species"""

    leveling_rate: LevelingRate = LevelingRate.INVALID
    base_exp_yield: int = -1
    effort_points: EffortValues = EffortValues(0, 0, 0, 0, 0, 0)
    # Bounded int in [0, 255]
    catch_rate: int = -1
    # Bounded int in [0, 255]
    base_friendship: int = -1
    # The chances of holding the item are 50%, 5% and 1% respectively.
    # If all three are the same item, then the chance of holding it is 100% instead.
    # wild_item_common: ItemId = ""
    # wild_item_uncommmon: ItemId = ""
    # wild_item_rare: ItemId = ""

    # evolutions: List[Evolution] = field(default_factory=lambda: [])

    def _asdict(self) -> Dict:
        return asdict(self)


@add_slots
@dataclass
class BreedingComponent:
    """Contains information about a breeding a pokemon, including egg cycles
    and gender information"""

    egg_groups: List[EggGroup] = field(default_factory=lambda: [EggGroup.INVALID])
    male_rate: Optional[float] = None
    # Hatch Time
    steps_to_hatch_lower: int = -1
    steps_to_hatch_upper: int = -1
    egg_cycles: int = -1

    def _asdict(self) -> Dict:
        return asdict(self)


@add_slots
@dataclass
class MoveComponent:
    """Information about the moves a variant can learn"""

    # Learn by level-up
    learned_moves: List[Tuple[int, MoveId]] = field(default_factory=lambda: [])
    tm_moves: List[Tuple[int, MoveId]] = field(default_factory=lambda: [])
    tr_moves: List[Tuple[int, MoveId]] = field(default_factory=lambda: [])
    egg_moves: List[MoveId] = field(default_factory=lambda: [])
    tutor_moves: List[MoveId] = field(default_factory=lambda: [])
    transfer_moves: List[MoveId] = field(default_factory=lambda: [])

    def _asdict(self) -> Dict:
        return asdict(self)


@add_slots
@dataclass
class DisplayComponent:
    """Information for displaying a pokemon"""

    battler_player_y: int = 0
    battler_enemy_y: int = 0
    battler_altitude: int = 0

    def _asdict(self) -> Dict:
        return asdict(self)


@add_slots
@dataclass
class Species:
    """Defines a "Pokemon species". It actually describes a variant
    of the species like Mega Salamance."""

    species_name: SpeciesId = ""
    variant_name: VariantId = ""

    base_stats: BaseStats = BaseStats(0, 0, 0, 0, 0, 0)

    dex_entry: DexEntryComponent = field(default_factory=lambda: DexEntryComponent())
    training_info: TrainingComponent = field(
        default_factory=lambda: TrainingComponent()
    )
    breeding_info: BreedingComponent = field(
        default_factory=lambda: BreedingComponent()
    )
    move_info: MoveComponent = field(default_factory=lambda: MoveComponent())
    display_info: DisplayComponent = field(default_factory=lambda: DisplayComponent())
    # Make abilities and hidden abilities properties
    # Make type a property

    def _asdict(self) -> Dict:
        return asdict(self)
