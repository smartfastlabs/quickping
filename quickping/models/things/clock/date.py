from datetime import date, datetime
from typing import TYPE_CHECKING

from quickping.utils.comparer import CallableComparer

if TYPE_CHECKING:
    from .clock import Clock


class Date:
    def __init__(self, clock: "Clock") -> None:
        self.clock = clock

    def __eq__(self, other: date) -> CallableComparer:  # type: ignore
        return CallableComparer(
            lambda: datetime.now().date() == other,
            things=[self.clock],
        )

    def __lt__(self, other: date) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().date() < other,
            things=[self.clock],
        )

    def __le__(self, other: date) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().date() <= other,
            things=[self.clock],
        )

    def __gt__(self, other: date) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().date() > other,
            things=[self.clock],
        )

    def __ge__(self, other: date) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().date() >= other,
            things=[self.clock],
        )
