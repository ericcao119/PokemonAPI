from typing import Dict, Any
from bson import ObjectId

from dataclasses import dataclass, field, asdict


@dataclass
class Ability:
    """This class represents the what an ability is. As most of the function of an ability is described in code,
    this class is rather sparse."""
    name: str = None
    description: str = None
    _id: ObjectId = field(default_factory=lambda: ObjectId())

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)
