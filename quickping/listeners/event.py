from collections.abc import Callable
from typing import Any

from .base import BaseListener


class EventListener(BaseListener):
    entity_filters: dict[str, Any]
    event_filter: str
    filter: Callable[[str, dict[str, Any]], bool] | None = None

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

            if callable(value) and not value(entity[key]):
                return False

            if entity[key] != value:
                return False

        return True
