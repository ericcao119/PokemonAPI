from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from bson import ObjectId
from src.data.poke_enums import EggGroup


@dataclass
class EggGroupList:
    """List of pokemon from a specific egg group"""
    group: EggGroup = EggGroup.INVALID
    pokemon_list: List[str] = field(default_factory=lambda: ObjectId())
    _id: ObjectId = field(default_factory=lambda: ObjectId())

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)
