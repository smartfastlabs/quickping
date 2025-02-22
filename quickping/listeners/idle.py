from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from quickping.models import Change, Thing

from .base import BaseListener


@dataclass
class IdleListener(BaseListener):
    func: Callable
    name: str
    things: list[Thing]
    timedelta: timedelta
    last_run: datetime | None = None

    def is_idle(self) -> bool:
        if not self.is_active():
            return False

        if self.last_run is None:
            return True

        return datetime.now() - self.last_run > self.timedelta

    async def on_change(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.last_run = datetime.now()

    def change_applies(self, change: Change) -> bool:
        if not self.is_active():
            return False

        return any(thing.id == change.thing_id for thing in self.things)
