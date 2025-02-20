from collections.abc import Callable

from quickping import listeners
from quickping.models import Thing


def on_change(
    *things: Thing,
) -> Callable:
    def decorator(func: Callable) -> listeners.ChangeListener:
        return listeners.ChangeListener(
            name=f"{func.__module__}.{func.__name__}",
            things=list(things),
            func=func,
        )

    return decorator
