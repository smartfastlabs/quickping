from datetime import datetime
from typing import Any

from quickping.models import Change

from .base import BaseListener


class IdleListener(BaseListener):
    def is_idle(self) -> bool:
        if not self.is_active():
            return False

        if not self.idle_time:
            return False

        if not self.last_run:
            return True
        return datetime.now() - self.last_run > self.idle_time

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
