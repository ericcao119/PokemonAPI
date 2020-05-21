"""Defines a pokemon ability"""

import dataclasses
from dataclasses import dataclass, field
from itertools import chain
from sqlite3 import Cursor
from typing import Any, Dict

from src.utils.general import add_slots


@add_slots
@dataclass
class Ability:
    """This class represents the what an ability is.
    As most of the function of an ability is described in code,
    this class is rather sparse."""

    ability_name: str = field(default_factory=lambda: "")
    effect: str = field(default_factory=lambda: "")
    description: str = field(default_factory=lambda: "")

    def _asdict(self) -> Dict[str, Any]:
        """Converts the class to a dict"""
        return dataclasses.asdict(self)

    def write_to_sql(self, cursor: Cursor):
        fields = [field.name for field in dataclasses.fields(self)]

        fields_str = ", ".join(fields)
        values_str = ", ".join("?" * len(fields))
        update_str = ",\n".join([f"{i}=?" for i in fields])
        entry_sql = (
            "INSERT OR REPLACE INTO\n\tAbility ("
            + fields_str
            + ")\nVALUES\n\t("
            + values_str
            + ") ON CONFLICT (ability_name) DO UPDATE SET\n"
            + update_str
            + ";"
        )
        # print(entry_sql)
        t = dataclasses.astuple(self)
        # print(t)
        cursor.execute(entry_sql, tuple(chain(t, t)))
