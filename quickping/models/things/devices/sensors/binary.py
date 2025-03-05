from typing import TYPE_CHECKING

from .sensor import Sensor

if TYPE_CHECKING:
    from quickping.utils.comparer import Comparer


class BinarySensor(Sensor):
    @property
    def is_triggered(self) -> "Comparer":
        return self.state == "on"

    @property
    def is_untriggered(self) -> "Comparer":
        return self.state == "off"
