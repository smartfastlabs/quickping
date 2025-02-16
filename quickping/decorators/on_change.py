from typing import List

from quickping import listeners
from quickping.models import Thing


def on_change(
    *things: List[Thing],
):
    def decorator(func):
        return listeners.ChangeListener(
            name=f"{func.__module__}.{func.__name__}",
            things=things,
            func=func,
        )

    return decorator
