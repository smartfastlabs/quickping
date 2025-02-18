from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar, Optional

from quickping.models.comparer import CallableComparer
from quickping.models.singletons import SingletonPerId

from .base import Base

if TYPE_CHECKING:
    from appdaemon.entity import Entity  # type: ignore

    from quickping.app import QuickpingApp


class Thing(Base, SingletonPerId):
    entity: Optional["Entity"] = None
    instances: ClassVar[dict[str, "Thing"]] = {}  # type: ignore

    def __init__(
        self,
        id: str,
        entity: Optional["Entity"] = None,
        quickping: Optional["QuickpingApp"] = None,
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

    def __getattr__(self, name: str) -> Any:
        if self.entity is None:
            return None
        return getattr(self.entity, name)

    def has(self, name: str) -> bool:
        if hasattr(self, name):
            return True
        if self.entity is None:
            return False
        return hasattr(self.entity, name)

    async def call_service(self, service: str, **kwargs: dict[str, Any]) -> None:
        if self.entity:
            await self.entity.call_service(service, **kwargs)

    async def turn_on(self) -> None:
        await self.call_service("turn_on")

    async def turn_off(self) -> None:
        await self.call_service("turn_off")

    async def toggle(self) -> None:
        if self.entity:
            await self.entity.toggle()

    def on_load(self) -> "Thing":
        if not self.quickping:
            raise ValueError("QuickpingApp not set on Thing")

        self.entity = self.quickping.get_entity(self.id)
        return self

    def is_(
        self, state: str | None = None, **kwargs: dict[str, Any]
    ) -> CallableComparer:
        def check() -> bool:
            if state is not None and self.state != state:
                return False

            for key, value in kwargs.items():
                if not self.has(key):
                    return False

                if getattr(self, key) != value:
                    return False

            return True

        return CallableComparer(check)

    def listen_state(self, func: Callable) -> None:
        if self.entity:
            self.entity.listen_state(func, self.entity)
        else:
            raise ValueError("Entity not set on Thing")

    @classmethod
    def get(cls, id: str) -> Optional["Thing"]:
        thing: SingletonPerId | None = cls.instances.get(id, None)
        if isinstance(thing, Thing):
            return thing

        return None
