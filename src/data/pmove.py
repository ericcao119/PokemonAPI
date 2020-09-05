"""Defines what a pokemon moves representation in the database is"""


# TODO: INITVAR to read from sqlite

import dataclasses
from dataclasses import asdict, astuple, dataclass, field, fields
from enum import Enum
from itertools import chain
from sqlite3 import Cursor
from typing import Any, Dict, Optional

from src.data.poke_enums import MoveCategory, PType, Target
from src.data.typing import ItemId
from src.utils.general import add_slots


@add_slots
@dataclass
class PMove:
    """Description of a move and its effects. """

    name: str = ""
    ptype: PType = PType.INVALID
    category: MoveCategory = MoveCategory.INVALID
    power: float = 0.0
    accuracy: float = 0.0
    pp: Optional[int] = None
    max_pp: int = 0
    generation_introduced: int = 0
    tm: Optional[int] = None
    tr: Optional[int] = None

    effect: str = field(default_factory=lambda: "")
    zmove_effect: Optional[str] = None

    description: str = field(default_factory=lambda: "")
    target_description: str = field(default_factory=lambda: "")

    def _asdict(self) -> Dict[str, Any]:
        """Converts the class to a dict"""
        return asdict(self)

    # def to_pokemon_essential(self):
    def write_to_sql(self, cursor: Cursor):
        fields = [field.name for field in dataclasses.fields(self)]

        fields_str = ", ".join(fields)
        values_str = ", ".join("?" * len(fields))
        update_str = ",\n".join([f"{i}=?" for i in fields])
        entry_sql = (
            "INSERT OR REPLACE INTO\n\tMove ("
            + fields_str
            + ")\nVALUES\n\t("
            + values_str
            + ") ON CONFLICT (name) DO UPDATE SET\n"
            + update_str
            + ";"
        )

        t = [str(i) if issubclass(type(i), Enum) else i for i in astuple(self)]
        # print(t)
        cursor.execute(entry_sql, tuple(chain(t, t)))


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
