from collections.abc import Callable
from typing import Any

from quickping import listeners


def on_event(event: str | None = None, **entity_filters: Any) -> Callable:
    def decorator(func: Callable) -> listeners.EventListener:
        return listeners.EventListener(
            name=f"{func.__module__}.{func.__name__}",
            event_filter=event,
            entity_filters=entity_filters,
            func=func,
        )

    return decorator
