import pymongo
from datetime import datetime
from typing import Dict, List, Any, field
from collections import namedtuple
from bson import ObjectId

from bson.codec_options import TypeCodec

Version = namedtuple('Version', 'version_num creation_date title author body tags')
@dataclass
class Diff:
    version_num: int
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    author: str
    tags_removed: List[str]
    tags_added: List[str] 
    body_update: Dict[str, Any]
    _id: ObjectId = field(default_factory=lambda:ObjectId())


@dataclass
class History:
    subject_id: ObjectId
    changes: List[Diff] = field(default_factory=lambda: [])
