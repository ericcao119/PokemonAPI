"""Defines what a pokemon moves representatino in the database is"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

from src.data.typing import ItemId
from src.data.poke_enums import PType, Target, MoveCategory
from src.utils.general import add_slots


@add_slots
@dataclass
class PMove:
    """Description of a move and its effects. """

    # TODO: Populate this
    name: str = ""
    ptype: PType = PType.INVALID
    category: MoveCategory = MoveCategory.INVALID
    power: int = 0
    accuracy: Optional[int] = None
    pp: int = 0
    tm: ItemId = field(default_factory=lambda: "")
    effect: str = field(default_factory=lambda: "")
    prob: Optional[int] = None

    def _asdict(self) -> Dict[str, Any]:
        """Converts the class to a dict"""
        return asdict(self)

    # def to_pokemon_essential(self):


@dataclass
class PMoveEssentials:
    """Pokemon Move as described in pokemon essentials. """

    # TODO: Populate this
    name: str = ""

    function_code: int = 0
    base_power: int = 0
    ptype: PType = PType.INVALID
    accuracy: int = 0
    total_pp: int = 0
    additional_effect_chance: int = 0
    target: Target = Target.INVALID
    priority: int = 0  # [-6, 6]

    # Flags
    # a - The move makes physical contact with the target.
    contact: bool = False
    # b - The target can use Protect or Detect to protect itself from the move.
    protectable: bool = False
    # c - The target can use Magic Coat to redirect the effect of the move.
    # Use this flag if the move deals no damage but causes a negative
    # effect on the target.
    # (Flags c and d are mutually exclusive.)
    magic_coat: bool = False
    # d - The target can use Snatch to steal the effect of the move.
    # Use this flag for most moves that target the user.
    # (Flags c and d are mutually exclusive.)
    snatch: bool = False
    mirror_move: bool = False  # e - The move can be copied by Mirror Move.
    # f - The move has a 10% chance of making the opponent flinch if the user
    # is holding a King's Rock/Razor Fang. Use this flag for all damaging
    # moves that don't already have a flinching effect.
    item_flinch: bool = False
    # g - If the user is frozen, the move will thaw it out before it is used.
    will_thaw: bool = False
    high_crit: bool = False  # h - The move has a high critical hit rate.
    # i - The move is a biting move (powered up by the ability Strong Jaw).
    biting: bool = False
    # j - The move is a punching move (powered up by the ability Iron Fist).
    punching: bool = False
    sound: bool = False  # k - The move is a sound-based move.
    # l - The move is a powder-based move (Grass-type Pokémon are
    # immune to them).
    powder: bool = False
    # m - The move is a pulse-based move (powered up by the ability
    # Mega Launcher).
    pulse: bool = False
    # n - The move is a bomb-based move (resisted by the ability Bulletproof).
    bomb: bool = False
    # Flags end

    description: str = ""

    def _asdict(self) -> Dict[str, Any]:
        """Converts the class to a dict"""
        return asdict(self)

    # def to_pokemon_essential(self):
