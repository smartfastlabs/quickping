from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Self

from quickping.models.singletons import SingletonPerId
from quickping.utils.comparer import CallableComparer, ValueComparer
from quickping.utils.meta import AttributesMeta

from .base import Base

if TYPE_CHECKING:
    from appdaemon.entity import Entity  # type: ignore

    from quickping.app import QuickpingApp


class Thing(Base, SingletonPerId, metaclass=AttributesMeta):
    entity: Optional["Entity"] = None
    instances: ClassVar[dict[str, "Thing"]] = {}  # type: ignore
    state: ValueComparer

    def __init__(
        self,
        _id: str,
        entity: Optional["Entity"] = None,
        quickping: Optional["QuickpingApp"] = None,
    ):
        if entity is None and quickping is not None:
            self.entity = quickping.get_entity(_id)
        else:
            self.entity = entity

        self.state = ValueComparer(
            "_state",
            entity=entity,
            thing=self,
        )
        super().__init__(_id, quickping)

    @property
    def _state(self) -> str:
        return self.entity.state if self.entity else "NA"

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

    async def call_service(self, service: str, **kwargs: Any) -> None:
        if self.entity:
            await self.entity.call_service(service, **kwargs)

    async def turn_on(self) -> None:
        await self.call_service("turn_on")

    async def turn_off(self) -> None:
        await self.call_service("turn_off")

    async def toggle(self) -> None:
        if self.entity:
            await self.entity.toggle()

    def on_load(self) -> Self:
        if not self.quickping:
            raise ValueError("QuickpingApp not set on Thing")

        self.entity = self.quickping.get_entity(self.id)
        return self

    def is_on(self) -> CallableComparer:
        return self.state == "on"

    def is_off(self) -> CallableComparer:
        return self.state == "off"

    def is_(
        self,
        state: str | None = None,
        **kwargs: Any,
    ) -> CallableComparer:
        def check() -> bool:
            if state is not None and self._state != state:
                return False

            for key, expected_value in kwargs.items():
                if not self.has(key):
                    return False

                if getattr(self, key) != expected_value:
                    return False

            return True

        return CallableComparer(check, things=[self])

    def listen_state(self, func: Callable) -> None:
        if self.entity:
            self.entity.listen_state(func)
        else:
            raise ValueError("Entity not set on Thing")

    @classmethod
    def get(cls, id: str) -> Optional["Thing"]:
        thing: SingletonPerId | None = cls.instances.get(id, None)
        if isinstance(thing, Thing):
            return thing

        return None
