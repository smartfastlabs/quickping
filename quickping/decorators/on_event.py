from typing import Any, Dict, Optional

from quickping import listeners


def on_event(event: Optional[str] = None, **entity_filters: Dict[str, Any]):
    def decorator(func):
        return listeners.EventListener(
            name=f"{func.__module__}.{func.__name__}",
            event_filter=event,
            entity_filters=entity_filters,
            func=func,
        )

    return decorator
