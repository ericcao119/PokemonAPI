"""Defines basic pokemon stats"""
from __future__ import annotations

from dataclasses import dataclass

from src.utils.general import add_slots


@add_slots
@dataclass
class BaseStats:
    """Stats to represent a pokemon's base stats"""

    hp: int
    attack: int
    defense: int
    speed: int
    special_attack: int
    special_defense: int

    @classmethod
    def valid_stat_value(cls, value):
        """Determines if the stat value is valid"""
        return 0 <= value <= 255

    def __setattr__(self, name, value):
        values = {
            "hp",
            "attack",
            "defense",
            "speed",
            "special_attack",
            "special_defense",
        }
        if name in values and not BaseStats.valid_stat_value(value):
            raise ValueError(f"Base stat {name}={value} not in range [0, 256)")

        self.__class__.__dict__[name].__set__(self, value)


@add_slots
@dataclass
class EffortValues:
    """Stats to represent effort values"""

    hp: int = 0
    attack: int = 0
    defense: int = 0
    speed: int = 0
    special_attack: int = 0
    special_defense: int = 0

    @classmethod
    def valid_stat_value(cls, value):
        """Determines if the stat value is valid"""
        return 0 <= value <= 3

    def __setattr__(self, name, value):
        values = {
            "hp",
            "attack",
            "defense",
            "speed",
            "special_attack",
            "special_defense",
        }
        if name in values and not EffortValues.valid_stat_value(value):
            raise ValueError(f"Base stat {name}={value} not in range [0, 4)")

        self.__class__.__dict__[name].__set__(self, value)

    @classmethod
    def from_string(cls, string: str) -> EffortValues:
        """Convert strings of a certain format into an EffortValues Object
        >>> EffortValues.from_string("1 Speed")
        EffortValues(hp=0, attack=0, defense=0, speed=1, special_attack=0, special_defense=0)
        >>> EffortValues.from_string(" 1      HP ,   2     Special Defense  ")
        EffortValues(hp=1, attack=0, defense=0, speed=0, special_attack=0, special_defense=2)
        """
        stats = string.split(",")
        stat_value = [int(i.split(maxsplit=1)[0]) for i in stats]
        stat_name = [
            (i.split(maxsplit=1)[1]).lower().strip().replace(" ", "_") for i in stats
        ]

        return EffortValues(**dict(zip(stat_name, stat_value)))
