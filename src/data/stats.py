from dataclasses import dataclass

from src.utils.general import add_slots


@add_slots
@dataclass
class BaseStats:
    HP: int
    Attack: int
    Defense: int
    Speed: int
    Special_Attack: int
    Special_Defense: int

    def __setattr__(self, name, value):
        values = {'HP', 'Attack', 'Defense', 'Speed',
                  'Special_Attack', 'Special_Defense'}
        if name in values and not self.valid_stat_value(value):
            raise ValueError(f'Base stat {name}={value} not in range [0, 256)')

        self.__class__.__dict__[name].__set__(self, value)

    def valid_stat_value(self, value):
        return 0 <= value <= 255


@add_slots
@dataclass
class EffortValues:
    HP: int
    Attack: int
    Defense: int
    Speed: int
    Special_Attack: int
    Special_Defense: int

    def __setattr__(self, name, value):
        values = {'HP', 'Attack', 'Defense', 'Speed',
                  'Special_Attack', 'Special_Defense'}
        if name in values and not self.valid_stat_value(value):
            raise ValueError(f'Base stat {name}={value} not in range [0, 4)')

        self.__class__.__dict__[name].__set__(self, value)

    def valid_stat_value(self, value):
        return 0 <= value <= 3
