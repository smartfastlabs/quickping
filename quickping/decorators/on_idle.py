from datetime import timedelta

from quickping import listeners
from quickping.models import Thing


def on_idle(
    timedelta: timedelta,
    *things: list[Thing],
):
    def decorator(func):
        listeners.IdleListener(
            func=func,
            name=f"{func.__module__}.{func.__name__}",
            things=things,
            timedelta=timedelta,
        )
        return func

    return decorator
