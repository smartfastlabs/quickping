import datetime
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from quickping.models import Thing
    from quickping.utils.comparer import Comparer

DEFAULT_LISTENERS: list["BaseListener"] = []


class BaseListener:
    name: str
    func: Callable
    instances: list["BaseListener"] = DEFAULT_LISTENERS
    quickping: Any = None
    disabled: bool = False
    whens: list["Comparer"]
    things: list["Thing"]
    after_time: datetime.time | None = None
    before_time: datetime.time | None = None

    def __init__(
        self,
        name: str,
        func: Callable,
        things: list["Thing"] | None = None,
        whens: list["Comparer"] | None = None,
        **kwargs: Any,
    ):
        self.name = name
        self.func = func
        self.whens = whens or []
        self.things = things or []

        if hasattr(func, "disabled"):
            self.disabled = func.disabled

        for key in ("before_time", "after_time", "disabled"):
            setattr(self, key, getattr(func, key, None))

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

    def add_when(self, when: "Comparer") -> Self:
        self.whens.append(when)
        self.update_things()
        return self

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

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
