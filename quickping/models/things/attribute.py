from typing import TYPE_CHECKING, Any, Optional

from quickping.models.comparer import CallableComparer
from quickping.utils.meta import AttributesMeta

if TYPE_CHECKING:
    from quickping.models.things.thing import Thing


class Attribute:
    entity: Any
    thing: "Thing"
    name: str
    value_type: type | None = None

    def __init__(
        self,
        name: str,
        entity: Any = None,
        thing: Optional["Thing"] = None,
        value_type: type | None = None,
    ):
        self.value_type = value_type
        self.entity = entity
        self.name = name
        if thing:
            self.thing = thing

    @property
    def value(self) -> Any:
        if self.entity is None:
            return
        if hasattr(self.entity, "attributes"):
            return getattr(self.entity.attributes, self.name)

    def __eq__(self, other: Any) -> CallableComparer:  # type: ignore
        return CallableComparer(
            lambda: self.value == other,
            things=[self.thing],
        )

    def __lt__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value < other,
            things=[self.thing],
        )

    def __le__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value <= other,
            things=[self.thing],
        )

    def __gt__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value > other,
            things=[self.thing],
        )

    def __ge__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value >= other,
            things=[self.thing],
        )


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
