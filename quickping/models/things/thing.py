from typing import TYPE_CHECKING, Any, ClassVar, Optional

from quickping.models.singletons import SingletonPerId
from quickping.utils.comparer import Comparer, ValueComparer
from quickping.utils.meta import AttributesMeta

from .base import Base

if TYPE_CHECKING:
    from quickping.app import QuickpingApp


class Thing(Base, SingletonPerId, metaclass=AttributesMeta):
    instances: ClassVar[dict[str, "Thing"]] = {}  # type: ignore

    state: ValueComparer

    _on_state: ClassVar[str] = "on"
    _off_state: ClassVar[str] = "off"

    _off_service: ClassVar[str] = "turn_off"
    _on_service: ClassVar[str] = "turn_on"

    def __init__(
        self,
        _id: str,
        quickping: Optional["QuickpingApp"] = None,
    ):
        super().__init__(_id, quickping)
        if not hasattr(self, "state"):
            # TODO: FIGURE OUT WHY WE NEED THE GUARD
            self.state = ValueComparer(
                thing=self,
            )

    async def call_service(self, service: str, **kwargs: Any) -> None:
        if not self.quickping:
            raise ValueError("QuickpingApp not set on Thing")

        await self.quickping.call_thing_service(
            service,
            thing_id=self.id,
            **kwargs,
        )

    async def turn_on(self) -> None:
        try:
            await self.call_service(self._on_service)
        except Exception as e:
            print(f"Error turning on {self}: {e}")

    async def turn_off(self) -> None:
        try:
            await self.call_service(self._off_service)
        except Exception as e:
            print(f"Error turning off {self}: {e}")

    async def toggle(self) -> None:
        await self.call_service("toggle")

    @property
    def is_on(self) -> Comparer:
        return self.state == self._on_state

    @property
    def is_off(self) -> Comparer:
        return self.state == self._off_state

    @classmethod
    def get(cls, _id: str) -> Optional["Thing"]:
        return cls.instances.get(_id, None)
