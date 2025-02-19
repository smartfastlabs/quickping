from inspect import isclass
from typing import TYPE_CHECKING, Optional

from .attribute import Attribute, Attributes

if TYPE_CHECKING:
    from quickping.app import QuickpingApp


class Base:
    id: str
    quickping: Optional["QuickpingApp"] = None

    def __init__(
        self,
        _id: str,
        quickping: Optional["QuickpingApp"] = None,
    ):
        self.id = _id
        self.quickping = quickping

    def load(self, qp: "QuickpingApp") -> "Base":
        self.quickping = qp
        result = self.on_load()

        for name, value in self.__annotations__.items():
            if value == Attribute:
                getattr(self, name).entity = qp.get_entity(self.id)

            elif isclass(value) and issubclass(value, Attributes):
                kwargs: dict[str, Attribute] = {}

                for attr_name, attr_anno in value.__annotations__.items():
                    value_type: type | None = None
                    if hasattr(attr_anno, "__metadata__"):
                        value_type = attr_anno.__metadata__[0]

                    kwargs[attr_name] = Attribute(
                        name,
                        entity=qp.get_entity(self.id),
                        value_type=value_type,
                    )
                setattr(self, name, value(**kwargs))

        return result

    def on_load(self) -> "Base":
        return self
