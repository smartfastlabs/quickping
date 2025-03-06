from typing import Annotated

from quickping.models.things.attribute import Attribute

from .device import Device


class Light(Device):
    # TODO: Make the name optional
    brightness: Annotated[Attribute, "brightness"]

    async def set_brightness(self, brightness: int) -> None:
        await self.call_service("turn_on", brightness=brightness)
