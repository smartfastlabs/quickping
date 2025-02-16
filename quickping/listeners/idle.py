from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, List, Optional

from ..models import Thing
from .base import BaseListener


@dataclass
class IdleListener(BaseListener):
    func: Callable
    name: str
    things: List[Thing]
    timedelta: timedelta
    last_run: datetime = datetime.now()

    def is_idle(self):
        if not self.is_active():
            return False
        if self.last_run is None:
            return True
        return datetime.now() - self.last_run > self.timedelta

    async def on_change(
        self,
        entity_id: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: dict,
    ):
        self.last_run = datetime.now()
