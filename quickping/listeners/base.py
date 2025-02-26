import datetime
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
            self.update_things()

        self.instances.append(self)

    def update_things(self) -> None:
        things: dict[str, "Thing"] = {}
        for when in self.whens:
            for thing in when.things:
                things[thing.id] = thing

        self.things = list(things.values())

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

        return all(self.whens)

    async def run(self, *args: Any, **kwargs: Any) -> Any:
        self.last_run = datetime.datetime.now()
        return await self.func(*args, **kwargs)
