from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quickping.models import Comparer, Thing

DEFAULT_LISTENERS: list["BaseListener"] = []


class BaseListener:
    name: str
    func: Callable
    instances: list["BaseListener"] = DEFAULT_LISTENERS
    quickping: Any = None
    disabled: bool = False
    whens: list["Comparer"]
    things: list["Thing"]

    def __init__(self, name: str, func: Callable, **kwargs: Any):
        self.name = name
        self.func = func
        self.whens = []
        self.things = []
        if hasattr(func, "disabled"):
            self.disabled = func.disabled
        if hasattr(func, "whens"):
            self.whens = func.whens
        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.__class__.instances is DEFAULT_LISTENERS:
            self.__class__.instances = []

        self.instances.append(self)

    @classmethod
    def clear(cls) -> None:
        cls.instances = DEFAULT_LISTENERS

    def is_active(self) -> bool:
        return (not self.disabled) and all(self.whens)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
