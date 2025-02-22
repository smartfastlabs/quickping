import asyncio
from datetime import datetime, time
from typing import Optional

from quickping.models.change import Change
from quickping.utils.comparer import CallableComparer

from .faux import FauxThing


class Clock(FauxThing):
    id: str = "clock"
    _instance: Optional["Clock"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance

        cls._instance = super().__new__(cls)
        return cls._instance

    async def run(self) -> None:
        return
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
            cls._instance = cls("clock")
        return [cls._instance]

    @classmethod
    def before(
        cls,
        am: int | None = None,
        pm: int | None = None,
        minute: int | None = None,
    ) -> "CallableComparer":
        # TODO HOW DO WE GET SELF HERE?
        t = time(
            hour=am if am is not None else pm + 12,
            minute=minute or 0,
        )

        def wrapper():
            {
                "last_time": datetime.now().time(),
            }

            def inner() -> bool:
                return datetime.now().time() < t

        return CallableComparer(
            lambda: datetime.now().time() < t,
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
