from collections.abc import Callable
from typing import Any

from .base import Comparer


class CallableComparer(Comparer):
    func: Callable

    def __init__(self, func: Callable, things: list[Any] | None | Callable = None):
        super().__init__(things=things)
        self.func = func

    def __bool__(self) -> bool:
        return bool(self.func())
