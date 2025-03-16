from collections.abc import Callable
from datetime import timedelta

from .collector import Collector


def run_every(
    seconds: float | timedelta | None = None,
    minutes: int | None = None,
    hours: int | None = None,
) -> Callable:
    def decorator(func: Callable | Collector) -> Collector:
        collector: Collector = func if isinstance(func, Collector) else Collector(func)

        if isinstance(seconds, timedelta):
            collector.run_on_interval = seconds
        else:
            collector.run_on_interval = timedelta(
                seconds=seconds or 0,
                minutes=minutes or 0,
                hours=hours or 0,
            )
        return collector

    return decorator
