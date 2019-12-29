"""Defines a pokemon ability"""

from typing import Dict, Any
from dataclasses import dataclass, asdict, field

from src.utils.general import add_slots


@add_slots
@dataclass
class Ability:
    """This class represents the what an ability is.
    As most of the function of an ability is described in code,
    this class is rather sparse."""
    name: str = field(default_factory=lambda: '')
    description: str = field(default_factory=lambda: '')

    def _asdict(self) -> Dict[str, Any]:
        """Converts the class to a dict"""
        return asdict(self)
