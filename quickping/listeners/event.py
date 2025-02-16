from typing import Any, Callable, Dict, Optional

from .base import BaseListener


class EventListener(BaseListener):
    entity_filters: Dict[str, Any]
    event_filter: str
    filter: Optional[Callable[[str, Dict[str, Any]], bool]] = None

    def wants_event(self, event: str, entity: dict) -> bool:
        if not self.is_active():
            return False

        if self.event_filter and event != self.event_filter:
            return False

        if self.filter:
            if self.filter(event, entity):
                return True

        elif not self.entity_filters:
            return True

        for key, value in self.entity_filters.items():
            if key not in entity:
                return False

            if callable(value):
                if not value(entity[key]):
                    return False

            if entity[key] != value:
                return False

        return True
