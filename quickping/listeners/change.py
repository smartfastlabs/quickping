from typing import Any, Callable, List, Optional

from appdaemon.entity import Entity

from ..models import Change, History, Thing
from .base import BaseListener


class ChangeListener(BaseListener):
    things: Optional[List[Thing]] = None
    history: Optional[History] = None

    async def on_change(
        self,
        thing_id: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: dict,
    ):
        if not self.is_active():
            return

        change = Change(
            thing_id=thing_id,
            attribute=attribute,
            old=old,
            new=new,
        )
        args = self.quickping.build_args(
            self.func,
            change=change,
            history=self.history,
        )
        await self.func(*args)

        if self.history is not None:
            self.history.add(change)
