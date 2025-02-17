from collections.abc import Callable
from dataclasses import dataclass, field


class Comparer:
    comparers: list["Comparer"]

    def __and__(self, other: "Comparer") -> "AndComparer":
        return AndComparer(comparers=[self, other])

    def __or__(self, other: "Comparer") -> "OrComparer":
        return OrComparer(comparers=[self, other])


class CallableComparer(Comparer):
    func: Callable

    def __init__(self, func: Callable):
        self.func = func

    def __bool__(self) -> bool:
        return bool(self.func())


@dataclass
class AndComparer(Comparer):
    comparers: list["Comparer"] = field(default_factory=list)

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

    def __bool__(self) -> bool:
        return any(comparer for comparer in self.comparers)

    def __and__(self, other: "Comparer") -> "AndComparer":
        return AndComparer(comparers=[self, other])

    def __or__(self, other: "Comparer") -> "OrComparer":
        self.comparers.append(other)
        return self
