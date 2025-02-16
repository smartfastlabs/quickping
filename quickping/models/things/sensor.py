from typing import Any, Optional

from appdaemon.entity import Entity

from ..comparer import CallableComparer


class SensorValue:
    entity: Optional[Entity] = None
    name: str

    def __init__(self, name: str):
        self.name = name

    @property
    def value(self) -> Any:
        if self.entity is None:
            return
        return getattr(self.entity.attributes, self.name)

    def __eq__(self, other):
        return CallableComparer(lambda: self.value == other)

    def __lt__(self, other):
        return CallableComparer(lambda: self.value < other)

    def __le__(self, other):
        return CallableComparer(lambda: self.value <= other)

    def __gt__(self, other):
        return CallableComparer(lambda: self.value > other)

    def __ge__(self, other):
        return CallableComparer(lambda: self.value >= other)
