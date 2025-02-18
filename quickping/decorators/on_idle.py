from collections.abc import Callable
from datetime import timedelta

from quickping import listeners
from quickping.models import Thing


def on_idle(
    timedelta: timedelta,
    *things: Thing,
) -> Callable:
    def decorator(func: Callable) -> listeners.IdleListener:
        return listeners.IdleListener(
            func=func,
            name=f"{func.__module__}.{func.__name__}",
            things=list(things),
            timedelta=timedelta,
        )

    return decorator
