"""Defines a item"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict

from src.utils.general import add_slots
from src.data.poke_enums import ItemCategory
from src.data.typing import ItemId


@add_slots
@dataclass
class Item:
    """This class represents the what an ability is.
    As most of the function of an ability is described in code,
    this class is rather sparse."""

    name: ItemId = field(default_factory=lambda: "")
    category: ItemCategory = ItemCategory.INVALID
    description: str = field(default_factory=lambda: "")

    def _asdict(self) -> Dict[str, Any]:
        """Converts the class to a dict"""
        return asdict(self)
