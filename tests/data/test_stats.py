import pytest

from src.data.stats import BaseStats


def test_base_stats_class():
    a = BaseStats(1, 2, 3, 4, 5, 6)
    assert(a.HP == 1)
    assert(a.Attack == 2)
    assert(a.Defense == 3)
    assert(a.Speed == 4)
    assert(a.Special_Attack == 5)
    assert(a.Special_Defense == 6)


def test_set_value():
    a = BaseStats(1, 2, 3, 4, 5, 6)
    a.Defense = 255
    assert(a.Defense == 255)


def test_set_invalid_value():
    a = BaseStats(1, 2, 3, 4, 5, 6)
    with pytest.raises(ValueError):
        a.Speed = -1

    with pytest.raises(ValueError):
        a.Speed = 256


def test_invalid_parameters():
    with pytest.raises(ValueError):
        BaseStats(0, 2, 3, 4, 5, 256)

    with pytest.raises(ValueError):
        BaseStats(0, 1, 2, 3, 4, -1)
