from quickping.models import Event

from .base import BaseListener


class EventListener(BaseListener):
    def wants_event(self, event: Event) -> bool:
        if not self.is_active():
            return False

        if self.event_filter and event.name != self.event_filter:
            return False

        elif not self.event_payload_filter:
            return True

        for key, value in self.event_payload_filter.items():
            if key not in event.data:
                return False

            if callable(value) and not value(event.data[key]):
                return False

            if event.data[key] != value:
                return False

        return True
