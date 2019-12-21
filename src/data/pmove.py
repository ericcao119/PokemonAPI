from dataclasses import dataclass, field, asdict
from bson import ObjectId
from typing import Dict, Any


@dataclass
class PMove:
    # TODO: Populate this

    _id: ObjectId = field(default_factory=lambda: ObjectId())

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)
