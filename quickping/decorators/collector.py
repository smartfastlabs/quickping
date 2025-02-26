from collections.abc import Callable
from datetime import time, timedelta
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from quickping.models import Thing
    from quickping.utils.comparer import Comparer


class Collector:
    days: list[int]
    event_payload_filter: dict[str, Any]
    func: Callable
    run_at: list[time]
    things: list["Thing"]
    whens: list["Comparer"]
    after_time: time | None = None
    before_time: time | None = None
    disabled: bool = False
    event_filter: str | None = None
    idle_time: timedelta | None = None
    route: str | None = None
    run_on_interval: timedelta | None = None
    instances: ClassVar[list["Collector"]] = []

    def __init__(self, func: Callable, **kwargs: Any):
        for key in (
            "whens",
            "things",
            "days",
            "run_at",
            "event_payload_filter",
        ):
            setattr(self, key, [])
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.func = func
        self.instances.append(self)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.func(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.func.__module__}.{self.func.__name__}"

    def get_listener_args(self) -> dict[str, Any]:
        return {
            "name": f"{self}",
            "func": self.func,
            "things": self.all_things(),
            "whens": self.whens,
            "run_at": self.run_at,
            "idle_time": self.idle_time,
            "route": self.route,
            "run_on_interval": self.run_on_interval,
            "event_filter": self.event_filter,
            "event_payload_filter": self.event_payload_filter,
        }

    def all_things(self) -> list["Thing"]:
        things: dict[str, "Thing"] = {}
        for thing in self.things:
            things[thing.id] = thing
        for when in self.whens:
            for thing in when.things:
                things[thing.id] = thing

        return list(things.values())

    @classmethod
    def clear(cls) -> None:
        cls.instances = []
