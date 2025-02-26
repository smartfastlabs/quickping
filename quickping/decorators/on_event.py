from collections.abc import Callable
from typing import Any

from .collector import Collector


def on_event(
    event: str | None = None,
    **event_payload_filter: Any,
) -> Callable:
    def decorator(func: Callable | Collector) -> Collector:
        if isinstance(func, Collector):
            func.event_filter = event
            func.event_payload_filter = event_payload_filter
            return func

        return Collector(
            func,
            event_filter=event,
            event_payload_filter=event_payload_filter,
        )

    return decorator
