import asyncio
from datetime import datetime, time
from typing import Optional

from quickping.models.change import Change
from quickping.utils.comparer import CallableComparer

from .faux import FauxThing


class Clock(FauxThing):
    id: str = "clock"
    _instance: Optional["Clock"] = None

    def __new__(cls) -> "Clock":
        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)
        return cls._instance

    async def run(self) -> None:
        old_time = datetime.now().time()
        while True:
            try:
                old_time = await self.loop(old_time)
            except Exception as e:
                print("CLOCK ERROR", e)

            await asyncio.sleep(0.1)

    async def loop(self, old_time: time) -> time:
        new_time = datetime.now().time()
        if old_time.second == new_time.second:
            return old_time

        if self.quickping:
            await self.quickping.on_change(
                Change(
                    thing_id=self.id,
                    old=time,
                    new=new_time,
                    attribute="time",
                )
            )
        return new_time

    @classmethod
    def things(cls) -> list["Clock"]:
        if not cls._instance:
            cls._instance = cls()
        return [cls._instance]

    @classmethod
    def before(
        cls,
        am: int | None = None,
        pm: int | None = None,
        minute: int | None = None,
    ) -> "CallableComparer":
        if am is None and pm is None:
            raise ValueError("Must provide either am or pm")
        # TODO HOW DO WE GET SELF HERE?
        t = time(
            hour=am if am is not None else pm + 12,  # type: ignore
            minute=minute or 0,
        )

        return CallableComparer(
            lambda: datetime.now().time() < t,
            # TODO: I think this could be things=[cls()]
            things=cls.things,
        )

    @classmethod
    def after(cls, t: time) -> "CallableComparer":
        return CallableComparer(
            lambda: datetime.now().time() > t,
            things=cls.things,
        )

    @classmethod
    def between(cls, start: time, end: time) -> "CallableComparer":
        return CallableComparer(
            lambda: start < datetime.now().time() < end,
            things=cls.things,
        )
