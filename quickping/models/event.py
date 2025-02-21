from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Event:
    name: str
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    thing_id: str | None = None
