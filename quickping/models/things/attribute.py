from typing import TYPE_CHECKING, Optional

from quickping.utils.comparer import ValueComparer
from quickping.utils.meta import AttributesMeta

if TYPE_CHECKING:
    from quickping.app import QuickpingApp
    from quickping.models.things.thing import Thing


class Attribute(ValueComparer):
    pass


class Attributes(metaclass=AttributesMeta):
    def __init__(
        self,
        thing: Optional["Thing"] = None,
        **kwargs: Attribute,
    ):
        for name, anno in self.__annotations__.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                setattr(
                    self,
                    name,
                    anno(
                        name,
                        thing=thing,
                    ),
                )

    def load(self, _: "QuickpingApp", thing: "Thing") -> None:
        self.thing = thing
        for _key, value in self.__dict__.items():
            if isinstance(value, Attribute):
                value.thing = thing
                value.entity = thing.entity
