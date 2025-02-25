from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from quickping import Thing
    from quickping.services import Service

    from .boolean import AndComparer, OrComparer


class Comparer:
    comparers: list["Comparer"]
    # TODO: THIS TYPING COULD BE WAY BETTER
    # I think we can just use any and pass in the objects and just use identity comparison
    _things: list["Thing"] | list["Service"] | Callable
    owner: Optional["Thing"]

    def __init__(
        self,
        comparers: list["Comparer"] | None = None,
        things: list["Thing"] | None | Callable = None,
    ):
        self.comparers = comparers or []
        self._things = things or []
        if things and not callable(things) and len(things) == 1:
            self.owner = things[0]

    @property
    def things(self) -> list[Any]:
        things = self._things() if callable(self._things) else self._things
        result: dict[str, Any] = {t.id: t for t in things}
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
