import pytest

from src.data.stats import BaseStats


def test_base_stats_class():
    a = BaseStats(1, 2, 3, 4, 5, 6)
    assert a.hp == 1
    assert a.attack == 2
    assert a.defense == 3
    assert a.speed == 4
    assert a.special_attack == 5
    assert a.special_defense == 6


def test_set_value():
    a = BaseStats(1, 2, 3, 4, 5, 6)
    a.defense = 255
    assert a.defense == 255


def test_set_invalid_value():
    a = BaseStats(1, 2, 3, 4, 5, 6)
    with pytest.raises(ValueError):
        a.speed = -1

    with pytest.raises(ValueError):
        a.speed = 256


def test_invalid_parameters():
    with pytest.raises(ValueError):
        BaseStats(0, 2, 3, 4, 5, 256)

    with pytest.raises(ValueError):
        BaseStats(0, 1, 2, 3, 4, -1)
