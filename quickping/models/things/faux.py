import asyncio
from typing import TYPE_CHECKING, ClassVar, Optional, Self

from quickping.models.things.thing import Thing

if TYPE_CHECKING:
    from quickping.app import QuickpingApp


class FauxThing(Thing):
    """Its not a real thing, but it acts like one."""

    id: str
    task: asyncio.Task | None = None
    quickping: Optional["QuickpingApp"] = None
    _running: ClassVar[bool] = False

    def __init__(
        self,
        _id: str,
        quickping: Optional["QuickpingApp"] = None,
    ):
        self.id = _id
        self.quickping = quickping

    @classmethod
    def start(cls, quickping: "QuickpingApp") -> None:
        """Run the faux thing."""
        cls.quickping = quickping

        if hasattr(cls, "run"):
            cls._running = True
            cls.task = asyncio.create_task(cls.run())

    @classmethod
    def stop(cls) -> None:
        print("Stopping faux thing", cls.__name__)
        cls._running = False

    def load(self, quickping: "QuickpingApp") -> Self:
        """Load the faux thing."""
        self.quickping = quickping

        if hasattr(self, "on_load"):
            self.on_load()

        return self

    @property
    def _state(self) -> str:
        return "on" if self.task else "off"

    def on_load(self) -> Self:
        """Called when the faux thing is loaded."""
        return self
