from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Optional

from .callable import CallableComparer

if TYPE_CHECKING:
    from quickping.models.things.thing import Thing


class ValueComparer:
    thing: Optional["Thing"] = None
    value: Any
    children: list["ValueComparer"]
    _value_history: list[tuple[datetime, Any]]

    def __init__(
        self,
        value: Any = None,
        thing: Optional["Thing"] = None,
    ):
        self._value_history = []
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

    def commit(self) -> None:
        self._value_history.append((datetime.now(), self.value))

    def history(
        self,
        look_back: timedelta | None = None,
    ) -> list[tuple[datetime, Any]]:
        if not look_back:
            return self._value_history

        start_time = datetime.now() - look_back
        result = []
        for time, value in self._value_history:
            if time < start_time:
                continue
            result.append((time, value))

        return result

    def _was(self, value: Any, look_back: timedelta) -> bool:
        return value in {h[1] for h in self.history(look_back)}

    def is_(self, value: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value == value,
            things=self.things,
        )

    def is_not(self, value: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value != value,
            things=self.things,
        )

    def was(self, value: Any, look_back: timedelta) -> CallableComparer:
        return CallableComparer(
            lambda: self._was(value, look_back),
            things=self.things,
        )

    def was_not(self, value: Any, look_back: timedelta) -> CallableComparer:
        return CallableComparer(
            lambda: not self._was(value, look_back),
            things=self.things,
        )
