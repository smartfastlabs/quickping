from typing import Annotated

from quickping.models.things.attribute import Attribute

from .device import Device


class Light(Device):
    pass


class FancyLight(Light):
    brightness: Annotated[Attribute, "brightness"]

    async def set_brightness(self, brightness: int) -> None:
        await self.call_service("turn_on", brightness=brightness)
