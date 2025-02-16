from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from .things import Thing


class Comparer:
    comparers: List["Comparer"]

    def __bool__(self):
        raise NotImplementedError

    def __and__(self, other: "Comparer") -> "AndComparer":
        return AndComparer(comparers=[self, other])

    def __or__(self, other: "Comparer") -> "OrComparer":
        return OrComparer(comparers=[self, other])

    @property
    def things(self) -> Dict[str, "Thing"]:
        result: Dict[str, "Thing"] = {}
        if hasattr(self, "thing"):
            result[self.thing.id] = self.thing

        for comparer in self.comparers:
            for key, value in comparer.things:
                result[key] = value

        return result


class CallableComparer(Comparer):
    func: callable

    def __init__(self, func: callable):
        self.func = func

    def __bool__(self) -> bool:
        return self.func()


# @dataclass
# class AttributeComparer(Comparer):
#     thing: "Thing"
#     checks: Dict[str, Any]

#     def __post_init__(self):
#         for key in self.checks.keys():
#             if not self.thing.has(key):
#                 raise AttributeError(
#                     f"{self.thing} does not have attribute {key}",
#                 )

#     def __bool__(self) -> bool:
#         for key, value in self.checks.items():
#             if not getattr(self.thing, key) == value:
#                 return False

#         return True


@dataclass
class AndComparer(Comparer):
    comparers: List["Comparer"] = field(default_factory=list)

    def __bool__(self) -> bool:
        return all(comparer for comparer in self.comparers)

    def __and__(self, other: "Comparer") -> "AndComparer":
        self.comparers.append(other)
        return self

    def __or__(self, other: "Comparer") -> "OrComparer":
        return OrComparer(comparers=[self, other])


@dataclass
class OrComparer(Comparer):
    comparers: List["Comparer"] = field(default_factory=list)

    def __bool__(self) -> bool:
        return any(comparer for comparer in self.comparers)

    def __and__(self, other: "Comparer") -> "AndComparer":
        return AndComparer(comparers=[self, other])

    def __or__(self, other: "Comparer") -> "OrComparer":
        self.comparers.append(other)
        return self
