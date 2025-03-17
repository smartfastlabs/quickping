import asyncio
from datetime import datetime, time, timedelta
from typing import TYPE_CHECKING, Any, Optional

from quickping.models.change import Change
from quickping.models.things.faux import FauxThing
from quickping.utils.clock import get_time
from quickping.utils.comparer import CallableComparer, Comparer

from .day import Day
from .hour import Hour

if TYPE_CHECKING:
    from quickping.app import QuickpingApp


class Clock(FauxThing):
    SUNDAY: int = 0
    MONDAY: int = 1
    TUESDAY: int = 2
    WEDNESDAY: int = 3
    THURSDAY: int = 4
    FRIDAY: int = 5
    SATURDAY: int = 6

    id: str = "clock"
    start_time: time | None = None
    end_time: time | None = None
    last_check: time | None = None
    last_tick: datetime | None = None
    tick_interval: timedelta | None = None

    def __init__(
        self,
        _id: str,
        quickping: Optional["QuickpingApp"] = None,
        start_time: time | None = None,
        end_time: time | None = None,
        tick_interval: timedelta | None = None,
    ) -> None:
        super().__init__(_id, quickping=quickping)
        self.start_time = start_time
        self.end_time = end_time
        self.last_check = datetime.now().time()
        self.tick_interval = tick_interval

    @property
    def hour(self) -> Hour:
        return Hour(Clock("clock.hourly"))

    @property
    def day(self) -> "Day":
        return Day(Clock("clock.daily"))

    @classmethod
    async def run(cls) -> None:
        last_time: time = datetime.now().time()
        while cls._running:
            try:
                new_time = datetime.now().time()
                await cls.loop(last_time)
                last_time = new_time

            except Exception as e:
                print("CLOCK ERROR", e)

            await asyncio.sleep(1)

    @classmethod
    async def loop(cls, old_time: time) -> None:
        now = datetime.now()
        new_time = now.time()
        if not cls.quickping:
            return

        promises = []
        for clock in cls.instances.values():
            if not isinstance(clock, Clock):
                continue

            if clock.is_triggered():
                promises.append(
                    cls.quickping.on_change(
                        Change(
                            thing_id=clock.id,
                            old=old_time,
                            new=new_time,
                            attribute="time",
                        ),
                    ),
                )
            elif clock.tick_interval is not None and (
                clock.last_tick is None
                or (now - clock.last_tick) >= clock.tick_interval
            ):
                promises.append(
                    cls.quickping.on_change(
                        Change(
                            thing_id=clock.id,
                            old=clock.last_tick,
                            new=now,
                            attribute="tick",
                        ),
                    ),
                )

                clock.last_tick = now
            clock.last_check = new_time

        await asyncio.gather(*promises)

    def is_triggered(self) -> bool:
        active: bool = self._is_active()

        was_active: bool = self._is_active(
            now=self.last_check,
        )

        return active != was_active

    def is_active(self) -> bool:
        return self._is_active()

    def __bool__(self) -> bool:
        return self.is_active()

    def _is_active(
        self,
        old_time: time | None = None,
        now: time | None = None,
    ) -> bool:
        if now is None:
            now = datetime.now().time()

        if self.start_time is not None and now < self.start_time:
            return False

        if self.end_time is not None and now > self.end_time:
            return False
        return True

    @property
    def comparer(self) -> CallableComparer:
        return CallableComparer(
            self._is_active,
            things=[self],
        )

    def __eq__(self, other: time) -> CallableComparer:  # type: ignore
        return self.between(
            start=time(other.hour, other.minute),
            end=time(other.hour, other.minute, 15),
        )

    @classmethod
    def tick(
        cls,
        dt: timedelta | None = None,
        minutes: int = 0,
        seconds: int = 0,
        hours: int = 0,
    ) -> CallableComparer:
        interval = dt or timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

        return cls(
            f"clock.tick.{interval}",
            tick_interval=interval,
        ).comparer

    def __lt__(self, other: time) -> CallableComparer:
        return self.before(other)

    def __le__(self, other: time) -> CallableComparer:
        return self.before(other)

    def __gt__(self, other: time) -> CallableComparer:
        return self.after(other)

    def __ge__(self, other: time) -> CallableComparer:
        return self.after(other)

    def before(self, *args: Any, **kwargs: Any) -> "CallableComparer":
        return self.clone(end_time=get_time(*args, **kwargs)).comparer

    def after(self, *args: Any, **kwargs: Any) -> "CallableComparer":
        return self.clone(start_time=get_time(*args, **kwargs)).comparer

    def between(self, start: time, end: time) -> "CallableComparer":
        return self.clone(
            start_time=start,
            end_time=end,
        ).comparer

    def clone(
        self,
        start_time: time | None = None,
        end_time: time | None = None,
        tick_interval: timedelta | None = None,
    ) -> "Clock":
        if start_time is not None:
            start_time = max(start_time, self.start_time or time(0, 0))
        if end_time is not None:
            end_time = min(end_time, self.end_time or time(23, 59))

        _id: str = "clock.clone."
        if self.start_time is not None:
            _id += f".start_{self.start_time.hour}:{self.start_time.minute}"
        if self.end_time is not None:
            _id += f".after_{self.end_time.hour}:{self.end_time.minute}"

        start_time = start_time or self.start_time
        end_time = end_time or self.end_time
        new_clock = self.__class__(f"clock.{start_time}-{end_time}|{tick_interval}")
        new_clock.start_time = start_time
        new_clock.end_time = end_time
        new_clock.tick_interval = tick_interval
        return new_clock

    @property
    def is_weekend(self) -> "CallableComparer":
        return CallableComparer(
            lambda: datetime.now().weekday() in [self.SATURDAY, self.SUNDAY],
            things=[Clock("clock.daily")],
        )

    @property
    def is_weekday(self) -> "CallableComparer":
        return CallableComparer(
            lambda: datetime.now().weekday() in range(self.MONDAY, self.FRIDAY),
            things=[Clock("clock.daily")],
        )

    def at(self, *args: time | int) -> Comparer:
        if isinstance(args[0], int):
            hour = args[0]
            minute = args[1] if len(args) > 1 else 0
            second = args[2] if len(args) > 2 else 0
            return self.__eq__(
                time(
                    hour=hour,
                    minute=minute,  # type: ignore
                    second=second,  # type: ignore
                )
            )

        result: Comparer = self.__eq__(args[0])
        for other in args[1:]:
            result |= self.__eq__(other)  # type: ignore
        return result
