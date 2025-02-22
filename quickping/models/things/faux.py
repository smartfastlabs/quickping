import asyncio
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from quickping.app import QuickpingApp


class FauxThing:
    """Its not a real thing, but it acts like one."""

    id: str
    task: asyncio.Task | None = None
    quickping: Optional["QuickpingApp"] = None

    def start(self, quickping: "QuickpingApp") -> None:
        """Run the faux thing."""
        self.quickping = quickping

        return
        if hasattr(self, "run"):
            self.task = asyncio.create_task(self.run())

    def load(self, quickping: "QuickpingApp") -> None:
        """Load the faux thing."""
        self.quickping = quickping

        if hasattr(self, "on_load"):
            self.on_load()
