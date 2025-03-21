from typing import TYPE_CHECKING

from .binary import BinarySensor

if TYPE_CHECKING:
    from quickping.utils.comparer import Comparer


class MotionSensor(BinarySensor):
    @property
    def is_moving(self) -> "Comparer":
        return self.state == "on"

    @property
    def is_still(self) -> "Comparer":
        return self.state == "off"
