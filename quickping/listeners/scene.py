from quickping.models import Event

from .base import BaseListener


class SceneListener(BaseListener):
    def wants_event(self, event: Event) -> bool:
        if not self.is_active():
            return False

        return (
            event.name == "call_service"
            and event.data["domain"] == "scene"
            and event.data["service"] == "turn_on"
            and event.data["service_data"]["entity_id"] == self.scene_id
        )
