from typing import TYPE_CHECKING, Any, Optional

from .callable import CallableComparer

if TYPE_CHECKING:
    from quickping.models.things.thing import Thing


class ValueComparer:
    thing: Optional["Thing"]
    name: str
    value_type: type | None = None

    def __init__(
        self,
        name: str,
        thing: Optional["Thing"] = None,
        value_type: type | None = None,
    ):
        self.value_type = value_type
        self.name = name
        self.thing = thing

    def things(self) -> list["Thing"]:
        if not self.thing:
            return []

        return [self.thing]

    @property
    def value(self) -> Any:
        if not self.thing:
            return None

        return self.thing.get_attribute(self.name)

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
