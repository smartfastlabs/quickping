from typing import TYPE_CHECKING

from .sensor import Sensor

if TYPE_CHECKING:
    from quickping.utils.comparer import Comparer


class MotionSensor(Sensor):
    @property
    def is_moving(self) -> "Comparer":
        return self.state == "on"

    @property
    def is_still(self) -> "Comparer":
        return self.state == "off"
