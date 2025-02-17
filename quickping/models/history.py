from collections.abc import Iterable
from datetime import datetime, timedelta

from quickping.models import Change


class History:
    def __init__(self, minutes: int):
        self.minutes = minutes
        self._changes: list[Change] = []

    def add(self, change: Change) -> None:
        self._changes.append(change)
        self.trim()

    def trim(self) -> list[Change]:
        now = datetime.now()
        td = timedelta(minutes=self.minutes)
        self._changes = [
            change for change in self._changes if change.timestamp > now - td
        ]
        return self._changes

    def __bool__(self) -> bool:
        return bool(self.trim())

    def __iter__(self) -> Iterable[Change]:
        return iter(self.trim())
