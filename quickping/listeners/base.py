import asyncio
import datetime
import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional

from quickping.decorators.collector import Collector

if TYPE_CHECKING:
    from quickping import QuickpingApp
    from quickping.models import Thing
    from quickping.utils.comparer import Comparer

DEFAULT_LISTENERS: list["BaseListener"] = []


class BaseListener(Collector):
    name: str
    instances: list["BaseListener"] = DEFAULT_LISTENERS  # type: ignore
    quickping: Any = None
    last_run: datetime.datetime

    def __init__(
        self,
        name: str,
        func: Callable,
        quickping: Optional["QuickpingApp"] = None,
        things: list["Thing"] | None = None,
        whens: list["Comparer"] | None = None,
        **kwargs: Any,
    ):
        # TODO: Make this work
        # super().__init__(func, things=things, **kwargs)
        self.quickping = quickping
        self.name = name
        self.func = func
        self.whens = whens or []
        self.things = things or []
        self.last_run = datetime.datetime.now()

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.__class__.instances is DEFAULT_LISTENERS:
            self.__class__.instances = []

        if whens:
            self.things = self.all_things()

        self.instances.append(self)

    @classmethod
    def clear(cls) -> None:
        cls.instances = DEFAULT_LISTENERS

    def is_active(self) -> bool:
        if self.disabled:
            return False
        if (
            self.after_time is not None
            and datetime.datetime.now().time() < self.after_time
        ):
            return False

        if (
            self.before_time is not None
            and datetime.datetime.now().time() > self.before_time
        ):
            return False

        return any(self.whens) if self.whens else True

    async def run(self, *args: Any, **kwargs: Any) -> Any:
        self.last_run = datetime.datetime.now()
        result: Any = await self.func(*args, **kwargs)

        if result and isinstance(result, tuple) and inspect.isawaitable(result[0]):
            return await asyncio.gather(*result)

        return result
