import dataclasses
from datetime import datetime
from typing import Any


@dataclasses.dataclass
class Change:
    thing_id: str
    attribute: str
    old: Any
    new: Any
    timestamp: datetime = dataclasses.field(default_factory=datetime.now)
