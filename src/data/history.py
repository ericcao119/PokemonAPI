import pymongo
from datetime import datetime
from typing import Dict, List, Any
from collections import namedtuple
from bson import ObjectId
from dataclasses import dataclass, field

from bson.codec_options import TypeCodec

Version = namedtuple('Version', 'version_num creation_date title author body tags')

@dataclass
class Diff:
    version_num: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    author: str = ''
    tags_removed: List[str] = field(default_factory=lambda: [])
    tags_added: List[str] = field(default_factory=lambda: [])
    body_update: Dict[str, Any] = field(default_factory=lambda: {})
    _id: ObjectId = field(default_factory=lambda:ObjectId())


@dataclass
class History:
    subject_id: ObjectId
    changes: List[Diff] = field(default_factory=lambda: [])
