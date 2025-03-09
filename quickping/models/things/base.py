from inspect import isclass
from typing import TYPE_CHECKING, Any, Optional, Self

from .attribute import Attribute, Attributes

if TYPE_CHECKING:
    from quickping.app import QuickpingApp


class Base:
    id: str
    quickping: Optional["QuickpingApp"] = None

    properties: dict[str, Any]

    def __init__(
        self,
        _id: str,
        quickping: Optional["QuickpingApp"] = None,
    ):
        self.id = _id
        self.quickping = quickping
        self.properties = {}

        # TODO: cleanup, document, understand
        for name, value in self.__annotations__.items():
            if isclass(value) and issubclass(value, Attributes):
                kwargs: dict[str, Attribute] = {}

                for attr_name in value.__annotations__:
                    kwargs[attr_name] = Attribute(
                        thing=self,  # type: ignore
                    )
                setattr(self, name, value(thing=self, **kwargs))  # type: ignore
            elif hasattr(value, "__origin__") and hasattr(value, "__metadata__"):
                # TODO: THIS CLAUSE IS A HACK, we should be
                # I KNOW for sure this can be an Attribute
                if issubclass(value.__origin__, Attribute):
                    setattr(
                        self,
                        name,
                        value.__origin__(
                            thing=self,
                        ),
                    )
                elif isinstance(value.__metadata__[0], value.__origin__):
                    setattr(self, name, value.__metadata__[0])
                elif isclass(value.__origin__):
                    # TODO: I'm not sure what this brnach is for
                    setattr(
                        self,
                        name,
                        value.__origin__(
                            value.__metadata__[0],
                            quickping=quickping,
                        ),
                    )

            elif not hasattr(self, name):
                setattr(self, name, None)

        if quickping:
            self.on_load()

    def load(self, qp: "QuickpingApp") -> Self:
        self.quickping = qp

        for name, _value in self.__annotations__.items():
            attr = getattr(self, name)
            if hasattr(attr, "load"):
                if isinstance(attr, Attributes):
                    attr.load(qp, thing=self)  # type: ignore
                else:
                    attr.load(qp)

        return self.on_load()

    def on_load(self) -> Self:
        return self
