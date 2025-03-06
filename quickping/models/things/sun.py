from typing import Annotated

from .attribute import Attribute
from .thing import Thing


class Sun(Thing):
    damn: Annotated[Attribute, "next_dawn"]
    dusk: Annotated[Attribute, "next_dusk"]
    sunrise: Annotated[Attribute, "next_rising"]
    sunset: Annotated[Attribute, "next_setting"]
