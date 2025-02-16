from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

from appdaemon.entity import Entity

from ..comparer import CallableComparer
from ..singletons import SingletonPerId
from .base import Base

if TYPE_CHECKING:
    from quickping.app import AppDaemonApp


class Thing(Base, SingletonPerId):
    entity: Optional[Entity] = None
    instances: dict[str, "Thing"] = {}

    def __init__(
        self,
        id: str,
        entity: Optional[Entity] = None,
        quickping: Optional["AppDaemonApp"] = None,
    ):
        super().__init__(id, quickping)
        self.entity = entity
        if entity is None and quickping is not None:
            self.entity = quickping.get_entity(id)

    @property
    def state(self) -> Any:
        if self.entity is None:
            return

        return self.entity.state

    def __getattr__(self, name):
        if self.entity is None:
            return None
        return getattr(self.entity, name)

    def has(self, name: str) -> bool:
        if hasattr(self, name):
            return True
        if self.entity is None:
            return False
        return hasattr(self.entity, name)

    async def call_service(self, service: str, **kwargs: Any):
        if self.entity is None:
            return

        await self.entity.call_service(service, **kwargs)

    async def turn_on(self):
        await self.call_service("turn_on")

    async def turn_off(self):
        await self.call_service("turn_off")

    async def toggle(self):
        if self.entity is None:
            return
        await self.entity.toggle()

    def on_load(self) -> "Thing":
        self.entity = self.quickping.get_entity(self.id)
        return self

    def is_(self, state: Optional[str] = None, **kwargs) -> CallableComparer:
        def check():
            if state is not None and self.state != state:
                return False

            for key, value in kwargs.items():
                if not self.has(key):
                    return False

                if getattr(self, key) != value:
                    return False

            return True

        return CallableComparer(check)
