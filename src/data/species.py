"""Dataclasses for describing a pokemon variant"""

from dataclasses import asdict, astuple, dataclass, field
from itertools import chain
from sqlite3 import Cursor
from typing import Dict, List, Optional, Tuple

from src.data.ability import Ability
from src.data.poke_enums import EvolutionType  # Habitat,
from src.data.poke_enums import Color, EggGroup, LevelingRate, PType, Shape
from src.data.stats import BaseStats, EffortValues
from src.data.typing import ItemId, MoveId, SpeciesId, VariantId
from src.utils.general import add_slots

REGIONAL_TEXT_MAPPING = {
    "(Red/Blue/Yellow)": "rby",
    "(Gold/Silver/Crystal)": "gsc",
    "(Ruby/Sapphire/Emerald)": "rse",
    "(FireRed/LeafGreen)": "frlg",
    "(Diamond/Pearl)": "dp",
    "(Platinum)": "plat",
    "(HeartGold/SoulSilver)": "hgss",
    "(Black/White)": "bw",
    "(Black 2/White 2)": "b2w2",
    "(X/Y — Mountain Kalos)": "xy_mountain",
    "(X/Y — Central Kalos)": "xy_central",
    "(X/Y — Coastal Kalos)": "xy_coastal",
    "(Omega Ruby/Alpha Sapphire)": "oras",
    "(Sun/Moon — Alola dex)": "sm",
    "(U.Sun/U.Moon — Alola dex)": "usum",
    "(Let's Go Pikachu/Let's Go Eevee)": "lets_go",
    "(Sword/Shield)": "swsh",
}


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
    national_dex_num: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    color: Color = Color.INVALID
    shape: Shape = Shape.INVALID
    kind: str = ""
    flavor_text: str = ""

    abilities: List[Ability] = field(default_factory=lambda: [])
    hidden_abilities: List[Ability] = field(default_factory=lambda: [])
    regional_dex_nums: Dict[str, int] = field(default_factory=lambda: {})

    def _asdict(self) -> Dict:
        return asdict(self)

    def get_regional_dex(self, key):
        return self.regional_dex_nums[key] if key in self.regional_dex_nums else None


@add_slots
@dataclass
class TrainingComponent:
    """Contains all variant information about training with/against a species"""

    leveling_rate: LevelingRate = LevelingRate.INVALID
    base_exp_yield: Optional[int] = None
    effort_points: Optional[EffortValues] = EffortValues(0, 0, 0, 0, 0, 0)
    # Bounded int in [0, 255]
    catch_rate: Optional[int] = None
    # Bounded int in [0, 255]
    base_friendship: Optional[int] = None
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
    steps_to_hatch_lower: Optional[int] = None
    steps_to_hatch_upper: Optional[int] = None
    egg_cycles: Optional[int] = None

    def _asdict(self) -> Dict:
        return asdict(self)

    def get_egg_group(self, idx: int) -> EggGroup:
        return self.egg_groups[idx] if len(self.egg_groups) > idx else EggGroup.INVALID


@add_slots
@dataclass
class MoveComponent:
    """Information about the moves a variant can learn"""

    # Learn by level-up
    learned_moves: List[Tuple[int, MoveId]] = field(default_factory=lambda: [])
    tm_moves: List[Tuple[int, MoveId]] = field(default_factory=lambda: [])
    tr_moves: List[Tuple[int, MoveId]] = field(default_factory=lambda: [])
    evolution_moves: List[MoveId] = field(default_factory=lambda: [])
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

    types: List[PType] = field(default_factory=lambda: [PType.INVALID, PType.INVALID])

    base_stats: BaseStats = BaseStats(0, 0, 0, 0, 0, 0)

    dex_entry: DexEntryComponent = field(default_factory=lambda: DexEntryComponent())
    training_info: TrainingComponent = field(
        default_factory=lambda: TrainingComponent()
    )
    breeding_info: BreedingComponent = field(
        default_factory=lambda: BreedingComponent()
    )
    move_info: MoveComponent = field(default_factory=lambda: MoveComponent())
    # display_info: DisplayComponent = field(default_factory=lambda: DisplayComponent())
    # Make abilities and hidden abilities properties
    # Make type a property

    def _asdict(self) -> Dict:
        return asdict(self)

    def get_type(self, idx: int) -> PType:
        return self.types[idx] if len(self.types) > idx else PType.INVALID

    def get_sql_tuple(self) -> Tuple:
        stats_tuple = (
            self.species_name,
            self.variant_name,
            str(self.get_type(0)),
            str(self.get_type(1)),
        ) + astuple(self.base_stats)

        dex_tuples: Tuple = (self.dex_entry.national_dex_num,)
        dex_tuples += tuple(
            self.dex_entry.get_regional_dex(i) for i in REGIONAL_TEXT_MAPPING.values()
        )

        dex_tuples += (
            self.dex_entry.height,
            self.dex_entry.weight,
            str(self.dex_entry.color),
            str(self.dex_entry.shape),
            self.dex_entry.kind,
            self.dex_entry.flavor_text,
        )

        training_tuples = (
            (str(self.training_info.leveling_rate), self.training_info.base_exp_yield)
            + (
                astuple(self.training_info.effort_points)
                if self.training_info.effort_points is not None
                else (None,) * 6
            )
            + (self.training_info.catch_rate, self.training_info.base_friendship)
        )

        breeding_tuples = (
            str(self.breeding_info.get_egg_group(0)),
            str(self.breeding_info.get_egg_group(1)),
            self.breeding_info.male_rate,
            self.breeding_info.steps_to_hatch_lower,
            self.breeding_info.steps_to_hatch_upper,
            self.breeding_info.egg_cycles,
        )

        return stats_tuple + dex_tuples + training_tuples + breeding_tuples

    def write_to_sql(self, cursor: Cursor):
        fields = [
            "species_name",
            "variant_name",
            "primary_type",
            "secondary_type",
            "hp",
            "attack",
            "defense",
            "speed",
            "special_attack",
            "special_defense",
            "national_dex_num",
            "rby_dex_num",
            "gsc_dex_num",
            "rse_dex_num",
            "frlg_dex_num",
            "dp_dex_num",
            "plat_dex_num",
            "hgss_dex_num",
            "bw_dex_num",
            "b2w2_dex_num",
            "xy_central_dex_num",
            "xy_coastal_dex_num",
            "xy_mountain_dex_num",
            "oras_dex_num",
            "sm_dex_num",
            "usum_dex_num",
            "lets_go_dex_num",
            "swsh_dex_num",
            "height_meters",
            "weight_kilos",
            "color",
            "shape",
            "kind",
            "flavor_text",
            "leveling_rate",
            "base_exp_yield",
            "effort_hp",
            "effort_attack",
            "effort_defense",
            "effort_speed",
            "effort_special_attack",
            "effort_special_defense",
            "catch_rate",
            "base_friendship",
            "primary_egg_group",
            "secondary_egg_group",
            "male_rate",
            "steps_to_hatch_lower",
            "steps_to_hatch_upper",
            "egg_cycles",
        ]

        fields_str = ", ".join(fields)
        values_str = ", ".join("?" * len(fields))
        update_str = ",\n".join([f"{i}=?" for i in fields])
        entry_sql = (
            "INSERT INTO\n\tSpecies ("
            + fields_str
            + ")\nVALUES\n\t("
            + values_str
            + ") ON CONFLICT (species_name, variant_name) DO UPDATE SET\n"
            + update_str
            + ";"
        )

        t = self.get_sql_tuple()
        cursor.execute(entry_sql, tuple(chain(t, t)))
