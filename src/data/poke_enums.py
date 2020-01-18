"""Defines basic enums for usin in pokemon dataclasses"""

import enum
import inspect
import sys


class PType(enum.Enum):
    """Defines the different pokemon types"""

    INVALID = -1
    Normal = 0
    Fire = 1
    Fighting = 2
    Water = 3
    Flying = 4
    Grass = 5
    Poison = 6
    Electric = 7
    Ground = 8
    Psychic = 9
    Rock = 10
    Ice = 11
    Bug = 12
    Dragon = 13
    Ghost = 14
    Dark = 15
    Steel = 16
    Fairy = 17

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class LevelingRate(enum.Enum):
    """Levelling rate of pokemon"""

    INVALID = -1
    Fast = 0
    Medium = 1
    MediumFast = 1
    Slow = 2
    MediumSlow = 3
    Parabolic = 3
    Erratic = 4
    Fluctuating = 5

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class EggGroup(enum.Enum):
    """Categorical variable of pokemon egg groups"""

    INVALID = -1
    Monster = 0
    Water1 = 1
    Bug = 2
    Flying = 3
    Field = 4
    Fairy = 5
    Grass = 6
    Humanlike = 7
    Water3 = 8
    Mineral = 9
    Amorphous = 10
    Water2 = 11
    Ditto = 12
    Dragon = 13
    Undiscovered = 14

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Color(enum.Enum):
    """Primary color of the pokemon"""

    INVALID = -1
    Black = 0
    Blue = 1
    Brown = 2
    Gray = 3
    Green = 4
    Pink = 5
    Purple = 6
    Red = 7
    White = 8
    Yellow = 9

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Shape(enum.Enum):
    """Defines the general shape of the pokemon"""

    INVALID = -1
    OnlyHead = 1
    Serpent = 2
    Fish = 3
    HeadArms = 4
    HeadBase = 5
    BipedalTail = 6
    HeadLegs = 7
    Quadruped = 8
    TwoWings = 9
    Tentacles_MultipleLegs = 10
    MultipleFusedBodies = 11
    Humanoid = 12
    WingedInsectoid = 13
    Insectoid = 14

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Habitat(enum.Enum):
    """Defines the habitat where a pokemon can live"""

    INVALID = -1
    Cave = 0
    Forest = 1
    Grassland = 2
    Mountain = 3
    Rare = 4
    RoughTerrain = 5
    Sea = 6
    Urban = 7
    WatersEdge = 8

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class EvolutionType(enum.Enum):
    """Defines the type of evoltion"""

    INVALID = -1
    Happiness = 0
    HappinessDay = 1
    HappinessNight = 2
    Level = 3
    Trade = 4
    TradeItem = 5
    Item = 6
    AttackGreater = 7
    AtkDefEqual = 8
    DefenseGreater = 9
    Silcoon = 10
    Cascoon = 11
    Ninjask = 12
    Shedinja = 13
    Beauty = 14
    ItemMale = 15
    ItemFemale = 16
    DayHoldItem = 17
    NightHoldItem = 18
    HasMove = 19
    HasInParty = 20
    LevelMale = 21
    LevelFemale = 22
    Location = 23
    TradeSpecies = 24
    LevelDay = 25
    LevelNight = 26
    LevelDarkInParty = 27
    LevelRain = 28
    HappinessMoveType = 29
    Custom1 = 30
    Custom2 = 31
    Custom3 = 32
    Custom4 = 33
    Custom5 = 34

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Target(enum.Flag):
    """Defines the target type for a move"""

    SELECT_TARGET = 0x00
    NO_TARGET = 0x01
    SINGLE_OPPOSING_RANDOM = 0x02
    ALL_OPPOSING = 0x04
    ALL_OTHER_THAN_USE = 0x08
    USER = 0x10
    BOTH_SIDES = 0x20
    USER_SIDE = 0x40
    OPPOSING_SIDE = 0x80
    USER_PARTNER = 0x100
    SINGLE_USER_SIDE = 0x200
    SINGLE_OPPOSING = 0x400
    SINGLE_OPPOSING_DIRECT_OPPOSITE = 0x800
    INVALID = 0x1000

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


POKE_ENUMS = [
    cls for (_, cls) in inspect.getmembers(sys.modules[__name__], inspect.isclass)
]
