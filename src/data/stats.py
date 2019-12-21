import pytest
from dataclasses import dataclass
from dataclasses import asdict



@dataclass
class Stats:
    __slots__ = ['HP', 'Attack', 'Defense', 'Speed', 'Special_Attack', 'Special_Defense']
    HP: int
    Attack: int
    Defense: int
    Speed: int
    Special_Attack: int
    Special_Defense: int

@dataclass
class BaseStats(Stats):
    __slots__ = []
    def __post_init__(self):
        member_vars = super().__slots__
        # print(member_vars)
        member_vals = [getattr(self, attr) for attr in member_vars]

        for var, val in zip(member_vars, member_vals):
            if not(self.valid_stat_value(val)):
                raise ValueError(f'Base stat {var}={val} not in range [0, 256)')
        
    
    def __setattr__(self, name, value):
        if name in super().__slots__:
            if not(self.valid_stat_value(value)):
                raise ValueError(f'Base stat {name}={value} not in range [0, 256)')
        super(BaseStats, self).__setattr__(name, value)

    def valid_stat_value(self, value):
        return 0 <= value <= 255

@dataclass
class EffortValues(Stats):
    __slots__ = []
    def __post_init__(self):
        member_vars = super().__slots__
        # print(member_vars)
        member_vals = [getattr(self, attr) for attr in member_vars]

        for var, val in zip(member_vars, member_vals):
            if not(self.valid_stat_value(val)):
                raise ValueError(f'Base stat {var}={val} not in range [0, 256)')
        
    
    def __setattr__(self, name, value):
        if name in super().__slots__:
            if not(self.valid_stat_value(value)):
                raise ValueError(f'Base stat {name}={value} not in range [0, 256)')
        super(EffortValues, self).__setattr__(name, value)

    def valid_stat_value(self, value):
        return 0 <= value <= 3
