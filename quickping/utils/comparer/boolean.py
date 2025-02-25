from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import Comparer

if TYPE_CHECKING:
    from quickping import Thing


@dataclass
class OrComparer(Comparer):
    comparers: list[Comparer] = field(default_factory=list)
    _things: list["Thing"] = field(default_factory=list)

    def __bool__(self) -> bool:
        return any(comparer for comparer in self.comparers)

    def __and__(self, other: Comparer) -> "AndComparer":
        return AndComparer(comparers=[self, other])

    def __or__(self, other: "Comparer") -> "OrComparer":
        self.comparers.append(other)
        return self


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
