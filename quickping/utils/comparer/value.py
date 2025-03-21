from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Optional

from .callable import CallableComparer

if TYPE_CHECKING:
    from quickping.models.things.thing import Thing


class ValueComparer:
    thing: Optional["Thing"] = None
    value: Any
    _value_history: list[tuple[datetime, Any]]

    def __init__(
        self,
        value: Any = None,
        thing: Optional["Thing"] = None,
    ):
        self._value_history = []
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

    def set_value(self, value: Any) -> None:
        print("Setting value to: ", value, id(self))
        self.value = value

    def commit(self) -> None:
        self._value_history.append((datetime.now(), self.value))

    def history(
        self,
        look_back: timedelta | None = None,
        end_td: timedelta | None = None,
    ) -> list[tuple[datetime, Any]]:
        now = datetime.now()
        result = []
        if look_back:
            start_time = now - look_back
            end_time = now - end_td if end_td else None
            for time, value in self._value_history:
                if time < start_time:
                    continue
                elif end_time and time > end_time:
                    break
                result.append((time, value))
        else:
            if end_td:
                end_time = now - end_td
                for time, value in self._value_history:
                    if time > end_time:
                        break
                    result.append((time, value))
            else:
                result = self._value_history

        return result

    def _was(
        self,
        value: Any,
        start_td: timedelta,
        end_td: timedelta | None = None,
    ) -> bool:
        datetime.now()
        return any(h == value for ts, h in self.history(start_td, end_td))

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
            lambda: self._was(value, look_back, timedelta(seconds=1)),
            things=self.things,
        )

    def was_not(self, value: Any, look_back: timedelta) -> CallableComparer:
        return CallableComparer(
            lambda: not self._was(value, look_back, timedelta(seconds=1)),
            things=self.things,
        )
