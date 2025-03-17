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

    @property
    def is_weekend(self) -> CallableComparer:
        return self.is_day(5, 6)

    @property
    def is_weekday(self) -> CallableComparer:
        return self.is_day(0, 1, 2, 3, 4)

    def is_day(self, *days: int) -> CallableComparer:
        return CallableComparer(
            lambda: datetime.now().weekday() in days,
            things=[self.clock],
        )

    @property
    def is_monday(self) -> CallableComparer:
        return self.is_day(0)

    @property
    def is_tuesday(self) -> CallableComparer:
        return self.is_day(1)

    @property
    def is_wednesday(self) -> CallableComparer:
        return self.is_day(2)

    @property
    def is_thursday(self) -> CallableComparer:
        return self.is_day(3)

    @property
    def is_friday(self) -> CallableComparer:
        return self.is_day(4)

    @property
    def is_saturday(self) -> CallableComparer:
        return self.is_day(5)

    @property
    def is_sunday(self) -> CallableComparer:
        return self.is_day(6)
