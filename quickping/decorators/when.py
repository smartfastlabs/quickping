from collections.abc import Callable

from quickping.utils.comparer import Comparer

from .collector import Collector


def when(*comparers: Comparer) -> Callable:
    def decorator(
        func: Callable | Collector,
    ) -> Collector:
        comparer = comparers[0]
        if len(comparers) > 1:
            for c in comparers[1:]:
                comparer = comparer & c

        collector: Collector = func if isinstance(func, Collector) else Collector(func)
        collector.whens.append(comparer)

        return collector

    return decorator
