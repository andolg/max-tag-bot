from dataclasses import dataclass
from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class Chat:
    name: str
    id: int

class TagOperation(Enum):
    AND = "AND"
    OR = "OR"

@dataclass
class Tag:
    name: str

@dataclass
class Message:
    message_id: str
    chat_id: int
    sender_id: Optional[int] = None
    tags: List[Tag] = field(default_factory=list)