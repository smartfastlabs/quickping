from typing import Annotated

from .attribute import Attribute
from .thing import Thing


class AWeather(Thing):
    temperature: Annotated[Attribute, "temperature"]
    humidity: Annotated[Attribute, "humidity"]
    uv: Annotated[Attribute, "uv_index"]
    clouds: Annotated[Attribute, "cloud_coverage"]
