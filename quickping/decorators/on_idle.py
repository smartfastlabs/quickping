from collections.abc import Callable
from datetime import timedelta

from quickping.models import Thing

from .collector import Collector


def on_idle(
    idle_time: timedelta,
    *things: Thing,
) -> Callable:
    def decorator(func: Callable | Collector) -> Collector:
        if isinstance(func, Collector):
            func.things.extend(things)
            func.idle_time = idle_time

        return Collector(
            func,
            things=things,
            idle_time=idle_time,
        )

    return decorator
