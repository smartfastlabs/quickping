from collections.abc import Callable

from quickping.models import Thing

from .collector import Collector


def on_change(
    *things: Thing,
) -> Callable:
    def decorator(func: Callable | Collector) -> Collector:
        collector: Collector = func if isinstance(func, Collector) else Collector(func)

        collector.things.extend(things)
        return collector

    return decorator
