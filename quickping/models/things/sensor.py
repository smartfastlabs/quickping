from typing import Any

from appdaemon.entity import Entity  # type: ignore

from quickping.models.comparer import CallableComparer


class SensorValue:
    entity: Entity | None = None
    name: str

    def __init__(self, name: str):
        self.name = name

    @property
    def value(self) -> Any:
        if self.entity is None:
            return
        return getattr(self.entity.attributes, self.name)

    def __eq__(self, other: Any) -> CallableComparer:  # type: ignore
        return CallableComparer(lambda: self.value == other)

    def __lt__(self, other: Any) -> CallableComparer:
        return CallableComparer(lambda: self.value < other)

    def __le__(self, other: Any) -> CallableComparer:
        return CallableComparer(lambda: self.value <= other)

    def __gt__(self, other: Any) -> CallableComparer:
        return CallableComparer(lambda: self.value > other)

    def __ge__(self, other: Any) -> CallableComparer:
        return CallableComparer(lambda: self.value >= other)
