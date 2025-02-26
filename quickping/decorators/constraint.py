from collections.abc import Callable
from datetime import time

from .collector import Collector


def constraint(
    before: time | None = None,
    after: time | None = None,
) -> Callable:
    def decorator(func: Callable | Collector) -> Collector:
        collector: Collector = func if isinstance(func, Collector) else Collector(func)
        if before is not None:
            collector.before_time = before
        if after is not None:
            collector.after_time = after
        return collector

    return decorator
