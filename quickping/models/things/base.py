from typing import TYPE_CHECKING, Any, Optional

from appdaemon.entity import Entity

from .sensor import SensorValue

if TYPE_CHECKING:
    from quickping.app import AppDaemonApp


class Base:
    id: str
    quickping: Optional["AppDaemonApp"] = None

    def __init__(
        self,
        id: str,
        quickping: Optional["AppDaemonApp"] = None,
    ):
        self.id = id
        self.quickping = quickping

    def load(self, qp: "AppDaemonApp") -> "Base":
        self.quickping = qp
        result = self.on_load()
        for name, value in self.__annotations__.items():
            if value == SensorValue:
                getattr(self, name).entity = qp.get_entity(self.id)

        return result

    def on_load(self) -> "Base":
        return self
