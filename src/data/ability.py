from typing import Dict, Any
from bson import ObjectId

from dataclasses import dataclass, field, asdict

@dataclass
class Ability:
    name: str = None
    description: str = None
    _id: ObjectId = field(default_factory=lambda:ObjectId())

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)