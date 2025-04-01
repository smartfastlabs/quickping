from collections.abc import Callable

from quickping.models import Thing
from quickping.utils.comparer import Comparer

from .collector import Collector


def daemon(*input: Comparer) -> Callable:
    def decorator(
        func: Callable | Collector,
    ) -> Collector:
        comparers: list[Comparer] = []
        things: list[Thing] = []
        for i in input:
            if isinstance(i, Comparer):
                comparers.append(i)
            elif isinstance(i, Thing):
                things.append(i)
            else:
                raise ValueError(f"Invalid input: {i}")

        collector: Collector = func if isinstance(func, Collector) else Collector(func)
        if comparers:
            comparer = comparers[0]
            for c in comparers[1:]:
                comparer = comparer & c

            collector.whens.append(comparer)
        collector.things.extend(things)

        return collector

    return decorator
