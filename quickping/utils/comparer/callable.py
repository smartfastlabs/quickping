from collections.abc import Callable
from typing import TYPE_CHECKING

from .base import Comparer

if TYPE_CHECKING:
    from quickping import Thing


class CallableComparer(Comparer):
    func: Callable

    def __init__(self, func: Callable, things: list["Thing"] | None | Callable = None):
        super().__init__(things=things)
        self.func = func

    def __bool__(self) -> bool:
        return bool(self.func())
