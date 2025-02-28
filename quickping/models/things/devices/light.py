from typing import Annotated

from quickping.models.things.attribute import Attribute

from .device import Device


class Light(Device):
    # TODO: Make the name optional
    brightness: Annotated[Attribute, "brightness"]
