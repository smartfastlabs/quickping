from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from quickping.models import Thing
    from quickping.utils.comparer import Comparer

DEFAULT_COLLECTORS: list["Collector"] = []


class Collector:
    days: list[int]
    event_payload_filter: dict[str, Any]
    func: Callable
    things: list["Thing"]
    whens: list["Comparer"]
    disabled: bool = False
    event_filter: str | None = None
    idle_time: timedelta | None = None
    route: str | None = None
    run_on_interval: timedelta | None = None
    scene_id: str | None = None
    instances: ClassVar[list["Collector"]] = DEFAULT_COLLECTORS

    def __init__(self, func: Callable, **kwargs: Any):
        for key in (
            "whens",
            "things",
            "days",
            "event_payload_filter",
        ):
            setattr(self, key, [])
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.func = func
        if self.__class__.instances is DEFAULT_COLLECTORS:
            self.__class__.instances = []

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
            "idle_time": self.idle_time,
            "route": self.route,
            "run_on_interval": self.run_on_interval,
            "event_filter": self.event_filter,
            "event_payload_filter": self.event_payload_filter,
            "scene_id": self.scene_id,
            "days": self.days,
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
        cls.instances = DEFAULT_COLLECTORS
