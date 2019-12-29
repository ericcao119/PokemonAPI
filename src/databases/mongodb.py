"""Basic mongodb specific information"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Any
from collections import namedtuple
from dataclasses import dataclass, field, asdict

from bson import ObjectId
from pymongo import MongoClient


Version = namedtuple("Version", "version_num creation_date title author body tags")


@dataclass
class Document:
    """A simple mongodb document"""

    _id: ObjectId = field(default_factory=lambda: ObjectId())
    data: Any = None

    @classmethod
    def fromdict(cls, mapping, data_type) -> Document:
        """Initialize class from dict"""
        return Document(_id=mapping["_id"], data=data_type(**mapping["data"]))

    def _asdict(self) -> Dict[str, Any]:
        """Convert class to dict"""
        return asdict(self)


@dataclass
class Diff:
    """Change made to a document"""

    version_num: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    author: str = ""
    tags_removed: List[str] = field(default_factory=lambda: [])
    tags_added: List[str] = field(default_factory=lambda: [])
    body_update: Dict[str, Any] = field(default_factory=lambda: {})
    _id: ObjectId = field(default_factory=lambda: ObjectId())


@dataclass
class History:
    """Represents history of changes made to a document"""

    subject_id: ObjectId
    changes: List[Diff] = field(default_factory=lambda: [])


def get_client() -> MongoClient:
    """Gets MongoDb client"""
    database = MongoClient()
    return database
