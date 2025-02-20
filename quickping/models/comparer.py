from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quickping import Thing


class Comparer:
    comparers: list["Comparer"]
    _things: list["Thing"]

    def __init__(
        self,
        comparers: list["Comparer"] | None = None,
        things: list["Thing"] | None = None,
    ):
        self.comparers = comparers or []
        self._things = things or []

    @property
    def things(self) -> list["Thing"]:
        result: dict[str, "Thing"] = {t.id: t for t in self._things}
        for comparer in self.comparers:
            for thing in comparer.things:
                result[thing.id] = thing
        return list(result.values())

    def __and__(self, other: "Comparer") -> "AndComparer":
        return AndComparer(comparers=[self, other])

    def __or__(self, other: "Comparer") -> "OrComparer":
        return OrComparer(comparers=[self, other])


class CallableComparer(Comparer):
    func: Callable

    def __init__(self, func: Callable, things: list["Thing"] | None = None):
        super().__init__(things=things)
        self.func = func

    def __bool__(self) -> bool:
        print(self.__dict__, "__bool__")
        return bool(self.func())


@dataclass
class AndComparer(Comparer):
    comparers: list["Comparer"] = field(default_factory=list)
    _things: list["Thing"] = field(default_factory=list)

    def __bool__(self) -> bool:
        return all(comparer for comparer in self.comparers)

    def __and__(self, other: "Comparer") -> "AndComparer":
        self.comparers.append(other)
        return self

    def __or__(self, other: "Comparer") -> "OrComparer":
        return OrComparer(comparers=[self, other])


@dataclass
class OrComparer(Comparer):
    comparers: list["Comparer"] = field(default_factory=list)
    _things: list["Thing"] = field(default_factory=list)

    def __bool__(self) -> bool:
        return any(comparer for comparer in self.comparers)

    def __and__(self, other: "Comparer") -> "AndComparer":
        return AndComparer(comparers=[self, other])

    def __or__(self, other: "Comparer") -> "OrComparer":
        self.comparers.append(other)
        return self
