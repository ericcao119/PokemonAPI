"""Defines an EggGroupList dataclass"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

from src.data.poke_enums import EggGroup
from src.utils.general import add_slots


@add_slots
@dataclass
class EggGroupList:
    """List of pokemon from a specific egg group"""
    group: EggGroup = EggGroup.INVALID
    pokemon_list: List[str] = field(default_factory=lambda: '')

    def _asdict(self) -> Dict[str, Any]:
        """Converts the class to a dict"""
        return asdict(self)
