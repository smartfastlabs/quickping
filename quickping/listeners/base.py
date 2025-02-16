from typing import TYPE_CHECKING, Any, Callable, List, Optional

if TYPE_CHECKING:
    from quickping.models import Comparable

DEFAULT_LISTENERS = []


class BaseListener:
    name: str
    func: Callable
    instances: Optional[List["BaseListener"]] = DEFAULT_LISTENERS
    quickping: Any = None
    disabled: bool = False
    whens: List["Comparable"] = []

    def __init__(self, name: str, func: Callable, **kwargs):
        self.name = name
        self.func = func
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
    def clear(cls):
        cls.instances = DEFAULT_LISTENERS

    def is_active(self):
        return (not self.disabled) and all(self.whens)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
