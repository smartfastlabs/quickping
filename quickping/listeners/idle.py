from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from quickping.models import Thing

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
        entity_id: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: dict,
    ) -> None:
        self.last_run = datetime.now()
