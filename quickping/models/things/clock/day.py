from datetime import datetime
from typing import TYPE_CHECKING

from quickping.utils.comparer import CallableComparer

if TYPE_CHECKING:
    from .clock import Clock


class Day:
    def __init__(self, clock: "Clock") -> None:
        self.clock = clock

    def __eq__(self, other: int) -> CallableComparer:  # type: ignore
        return CallableComparer(
            lambda: datetime.now().weekday() == other,
            things=[self.clock],
        )

    def __lt__(self, other: int) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().weekday() < other,
            things=[self.clock],
        )

    def __le__(self, other: int) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().weekday() <= other,
            things=[self.clock],
        )

    def __gt__(self, other: int) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().weekday() > other,
            things=[self.clock],
        )

    def __ge__(self, other: int) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().weekday() >= other,
            things=[self.clock],
        )
