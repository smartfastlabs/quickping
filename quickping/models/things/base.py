from typing import TYPE_CHECKING, Optional

from .sensor import SensorValue

if TYPE_CHECKING:
    from quickping.app import QuickpingApp


class Base:
    id: str
    quickping: Optional["QuickpingApp"] = None

    def __init__(
        self,
        _id: str,
        quickping: Optional["QuickpingApp"] = None,
    ):
        self.id = _id
        self.quickping = quickping

    def load(self, qp: "QuickpingApp") -> "Base":
        self.quickping = qp
        result = self.on_load()
        for name, value in self.__annotations__.items():
            if value == SensorValue:
                getattr(self, name).entity = qp.get_entity(self.id)

        return result

    def on_load(self) -> "Base":
        return self
