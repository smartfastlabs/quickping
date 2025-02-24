import asyncio
import uuid
from datetime import datetime, time
from typing import Any

from quickping.models.change import Change
from quickping.utils.clock import get_time
from quickping.utils.comparer import CallableComparer

from .faux import FauxThing


class Clock(FauxThing):
    id: str = "clock"
    start_time: time | None = None
    end_time: time | None = None
    last_check: time | None = None

    @classmethod
    async def run(cls) -> None:
        last_time: time = datetime.now().time()
        while True:
            try:
                new_time = datetime.now().time()
                await cls.loop(last_time)
                last_time = new_time

            except Exception as e:
                print("CLOCK ERROR", e)

            await asyncio.sleep(0.1)

    @classmethod
    async def loop(cls, old_time: time) -> None:
        new_time = datetime.now().time()
        if not cls.quickping:
            return

        promises = []
        for clock in cls.instances.values():
            if not isinstance(clock, Clock):
                continue

            clock.last_check = new_time
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

        await asyncio.gather(*promises)

    def is_triggered(self) -> bool:
        return self._is_active(old_time=self.last_check)

    def is_active(self) -> bool:
        return self._is_active()

    def __bool__(self) -> bool:
        return self.is_active()

    def _is_active(
        self,
        old_time: time | None = None,
    ) -> bool:
        now: time = datetime.now().time()

        result: bool = True
        if self.start_time is not None:
            if now >= self.start_time:
                if old_time:
                    result = old_time < self.start_time
                result = True
            else:
                return False

        if not result:
            return False

        if self.end_time is not None:
            if now <= self.end_time:
                if old_time:
                    result = old_time < self.end_time
                result = True
            else:
                return False

        return result

    @property
    def comparer(self) -> CallableComparer:
        return CallableComparer(
            self._is_active,
            things=[self],
        )

    def __eq__(self, other: time) -> CallableComparer:  # type: ignore
        return self.clone(
            start_time=other,
            end_time=other,
        ).comparer

    def __lt__(self, other: time) -> CallableComparer:
        print("LT", other, id(self), self.id, self.start_time, self.end_time)
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

        new_clock = self.__class__(f"clock.clone.{uuid.uuid4()}")
        if start_time is not None:
            new_clock.start_time = start_time
        if end_time is not None:
            new_clock.end_time = end_time
        return new_clock
