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
                print(thing.id, thing)
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
        return (not self.disabled) and all(self.whens)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
