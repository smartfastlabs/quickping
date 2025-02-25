from typing import Self

from quickping.models.things.thing import Thing
from quickping.services.base import Service


class FauxThing(Service, Thing):
    """Its not a real thing, but it acts like one."""

    @property
    def state(self) -> str:
        return "on" if self.task else "off"

    def on_load(self) -> Self:
        """Called when the faux thing is loaded."""
        return self
