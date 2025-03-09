from typing import TYPE_CHECKING, Any, Optional

from .callable import CallableComparer

if TYPE_CHECKING:
    from quickping.models.things.thing import Thing


class ValueComparer:
    thing: Optional["Thing"] = None
    value: Any
    children: list["ValueComparer"]

    def __init__(
        self,
        value: Any = None,
        thing: Optional["Thing"] = None,
    ):
        self.children = []
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
        print("Cloning", id(self))
        result = self.__class__(self.value, thing=self.thing)
        self.children.append(result)

        return result

    def set_value(self, value: Any) -> None:
        # TODO: FIGURE OUT IF WE NEED TO TRACK CHILDREN
        print("Setting value to: ", value, id(self))
        self.value = value
        for child in self.children:
            print("Setting value on child", child)
            child.set_value(value)
