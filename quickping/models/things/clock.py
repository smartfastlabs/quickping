from datetime import datetime, time
from typing import Optional

from quickping.utils.comparer import CallableComparer

from .faux import FauxThing


class Clock(FauxThing):
    _instance: Optional["Clock"] = None

    @classmethod
    def things(cls) -> list["Clock"]:
        if not cls._instance:
            cls._instance = cls("clock")
        return [cls._instance]

    @classmethod
    def before(cls, t: time) -> "CallableComparer":
        # TODO HOW DO WE GET SELF HERE?
        return CallableComparer(
            lambda: datetime.now().time() < t,
            things=cls.things,
        )

    @classmethod
    def after(cls, t: time) -> "CallableComparer":
        # TODO HOW DO WE GET SELF HERE?
        return CallableComparer(
            lambda: datetime.now().time() > t,
            things=cls.things,
        )

    @classmethod
    def between(cls, start: time, end: time) -> "CallableComparer":
        # TODO HOW DO WE GET SELF HERE?
        return CallableComparer(
            lambda: start < datetime.now().time() < end,
            things=cls.things,
        )
