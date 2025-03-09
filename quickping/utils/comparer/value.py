from typing import TYPE_CHECKING, Any, Optional

from .callable import CallableComparer

if TYPE_CHECKING:
    from quickping.models.things.thing import Thing


class ValueComparer:
    thing: Optional["Thing"] = None
    value: Any

    def __init__(
        self,
        value: Any = None,
        thing: Optional["Thing"] = None,
    ):
        self.value = value
        self.thing = thing

    def things(self) -> list["Thing"]:
        if not self.thing:
            return []

        return [self.thing]

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

    def clone(self) -> "ValueComparer":
        return self.__class__(self.value, thing=self.thing)
