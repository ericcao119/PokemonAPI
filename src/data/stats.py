"""Defines basic pokemon stats"""

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

    def __setattr__(self, name, value):
        values = {
            "hp",
            "attack",
            "defense",
            "speed",
            "special_attack",
            "special_defense",
        }
        if name in values and not self.valid_stat_value(value):
            raise ValueError(f"Base stat {name}={value} not in range [0, 256)")

        self.__class__.__dict__[name].__set__(self, value)

    def valid_stat_value(self, value):
        """Determines if the stat value is valid"""
        return 0 <= value <= 255


@add_slots
@dataclass
class EffortValues:
    """Stats to represent effort values"""
    hp: int
    attack: int
    defense: int
    speed: int
    special_attack: int
    special_defense: int

    def __setattr__(self, name, value):
        values = {
            "hp",
            "attack",
            "defense",
            "speed",
            "special_attack",
            "special_defense",
        }
        if name in values and not self.valid_stat_value(value):
            raise ValueError(f"Base stat {name}={value} not in range [0, 4)")

        self.__class__.__dict__[name].__set__(self, value)

    def valid_stat_value(self, value):
        """Determines if the stat value is valid"""
        return 0 <= value <= 3
