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

        for name, value in self.__annotations__.items():
            if isclass(value) and issubclass(value, Attributes):
                kwargs: dict[str, Attribute] = {}

                for attr_name, attr_anno in value.__annotations__.items():
                    value_type: type | None = None
                    if hasattr(attr_anno, "__metadata__"):
                        value_type = attr_anno.__metadata__[0]

                    kwargs[attr_name] = Attribute(
                        name,
                        entity=quickping.get_entity(self.id) if quickping else None,
                        thing=self,  # type: ignore
                        value_type=value_type,
                    )
                setattr(self, name, value(thing=self, **kwargs))  # type: ignore
            elif hasattr(value, "__origin__") and hasattr(value, "__metadata__"):
                # TODO: THIS CLAUSE IS A HACK, we should be
                # I KNOW for sure this can be an Attribute
                entity = quickping.get_entity(self.id) if quickping else None
                if issubclass(value.__origin__, Attribute):
                    setattr(
                        self,
                        name,
                        value.__origin__(
                            name,
                            entity=entity,
                            thing=self,
                            value_type=value.__metadata__[0],
                        ),
                    )
                elif isinstance(value.__metadata__[0], value.__origin__):
                    setattr(self, name, value.__metadata__[0])
                elif isclass(value.__origin__):
                    setattr(
                        self,
                        name,
                        value.__origin__(
                            value.__metadata__[0],
                            entity=entity,
                            quickping=quickping,
                        ),
                    )

            elif not hasattr(self, name):
                setattr(self, name, None)

        if quickping:
            self.on_load()

    def load(self, qp: "QuickpingApp") -> "Base":
        self.quickping = qp

        for name, _value in self.__annotations__.items():
            attr = getattr(self, name)
            if hasattr(attr, "entity") and attr.entity is None:
                attr.entity = qp.get_entity(self.id)
            if hasattr(attr, "load"):
                attr.load(qp)

        return self.on_load()

    def on_load(self) -> "Base":
        return self
