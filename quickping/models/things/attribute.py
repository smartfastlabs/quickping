from typing import Any

from quickping.models.comparer import CallableComparer
from quickping.utils.meta import AttributesMeta


class Attribute:
    entity: Any
    name: str
    value_type: type | None = None

    def __init__(
        self,
        name: str,
        entity: Any = None,
        value_type: type | None = None,
    ):
        self.value_type = value_type
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


class Attributes(metaclass=AttributesMeta):
    def __init__(self, **kwargs: Attribute):
        for name, anno in self.__annotations__.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                setattr(
                    self,
                    name,
                    anno(
                        name,
                    ),
                )
