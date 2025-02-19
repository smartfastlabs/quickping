from typing import Any

from quickping.models.comparer import CallableComparer


class SensorValue:
    entity: Any
    name: str

    def __init__(self, name: str, entity: Any = None):
        self.entity = entity
        self.name = name

    @property
    def value(self) -> Any:
        if self.entity is None:
            return
        if hasattr(self.entity, "attributes"):
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
