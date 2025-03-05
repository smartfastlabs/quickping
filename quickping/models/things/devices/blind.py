from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quickping.utils.comparer import Comparer

from .device import Device


class Blind(Device):
    @property
    def is_open(self) -> "Comparer":
        return self.state == "open"

    @property
    def is_closed(self) -> "Comparer":
        return self.state == "closed"
