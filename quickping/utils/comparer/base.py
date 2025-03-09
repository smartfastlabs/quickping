from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quickping import Thing

    from .boolean import AndComparer, OrComparer


class Comparer:
    comparers: list["Comparer"]
    _things: list["Thing"] | Callable

    def __init__(
        self,
        comparers: list["Comparer"] | None = None,
        things: list["Thing"] | None | Callable = None,
    ):
        self.comparers = comparers or []
        self._things = things or []

    @property
    def things(self) -> list["Thing"]:
        things = self._things() if callable(self._things) else self._things
        result: dict[str, "Thing"] = {t.id: t for t in things}
        for comparer in self.comparers or []:
            for thing in comparer.things:
                result[thing.id] = thing
        return list(result.values())

    def __and__(self, other: "Comparer") -> "AndComparer":
        from .boolean import AndComparer

        return AndComparer(comparers=[self, other])

    def __or__(self, other: "Comparer") -> "OrComparer":
        from .boolean import OrComparer

        return OrComparer(comparers=[self, other])

    def __invert__(self) -> "Comparer":
        return self.no_trigger()

    def no_trigger(self) -> "Comparer":
        result = self.clone()
        result._things = []
        return result

    def clone(self) -> "Comparer":
        return self.__class__(
            comparers=self.comparers,
            things=self._things,
        )
