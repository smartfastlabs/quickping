from typing import TYPE_CHECKING, Any, Optional

from quickping.utils.comparer import CallableComparer
from quickping.utils.meta import AttributesMeta

if TYPE_CHECKING:
    from quickping.app import QuickpingApp
    from quickping.models.things.thing import Thing


class Attribute:
    entity: Any
    thing: Optional["Thing"]
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
        self.thing = thing

    def things(self) -> list["Thing"]:
        if not self.thing:
            print("NO THING")
            return []

        return [self.thing]

    @property
    def value(self) -> Any:
        if self.entity is None:
            return
        if hasattr(self.entity, "attributes"):
            return getattr(self.entity.attributes, self.name)

    def __eq__(self, other: Any) -> CallableComparer:  # type: ignore
        return CallableComparer(
            lambda: self.value == other,
            things=self.things,
        )

    def __lt__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value < other,
            things=self.things,
        )

    def __le__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value <= other,
            things=self.things,
        )

    def __gt__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value > other,
            things=self.things,
        )

    def __ge__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value >= other,
            things=self.things,
        )


class Attributes(metaclass=AttributesMeta):
    def __init__(
        self,
        thing: Optional["Thing"] = None,
        **kwargs: Attribute,
    ):
        for name, anno in self.__annotations__.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                setattr(
                    self,
                    name,
                    anno(
                        name,
                        thing=thing,
                    ),
                )

    def load(self, _: "QuickpingApp", thing: "Thing") -> None:
        self.thing = thing
        for _key, value in self.__dict__.items():
            if isinstance(value, Attribute):
                value.thing = thing
                value.entity = thing.entity
