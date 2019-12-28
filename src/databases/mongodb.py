from datetime import datetime
from pymongo import MongoClient
from typing import Dict, List, Any
from dataclasses import dataclass, field, asdict
from bson import ObjectId


from collections import namedtuple

Version = namedtuple(
    'Version', 'version_num creation_date title author body tags')


@dataclass
class Document:
    _id: ObjectId = field(default_factory=lambda: ObjectId())
    data: Any

    @classmethod
    def fromdict(cls, mapping, data_type) -> Document:
        return Document(_id=mapping['_id'], data=data_type(**mapping['data']))

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Diff:
    version_num: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    author: str = ''
    tags_removed: List[str] = field(default_factory=lambda: [])
    tags_added: List[str] = field(default_factory=lambda: [])
    body_update: Dict[str, Any] = field(default_factory=lambda: {})
    _id: ObjectId = field(default_factory=lambda: ObjectId())


@dataclass
class History:
    subject_id: ObjectId
    changes: List[Diff] = field(default_factory=lambda: [])


db = MongoClient()
