from typing import Any

from quickping.models.comparer import CallableComparer


class Attribute:
    parent: Any
    name: str
    value_type: type | None = None

    def __init__(
        self,
        name: str,
        entity: Any = None,
        value_type: type | None = None,
    ):
        self.value_type = value_type
        self.entity = entity
        self.name = name

    @property
    def value(self) -> Any:
        if self.parent is None:
            return
        if hasattr(self.parent, "attributes"):
            return getattr(self.parent.attributes, self.name)

    def __eq__(self, other: Any) -> CallableComparer:  # type: ignore
        return CallableComparer(lambda: self.value == other)

    def __lt__(self, other: Any) -> CallableComparer:
        return CallableComparer(lambda: self.value < other)

    def __le__(self, other: Any) -> CallableComparer:
        return CallableComparer(lambda: self.value <= other)

    def __gt__(self, other: Any) -> CallableComparer:
        return CallableComparer(lambda: self.value > other)

    def __ge__(self, other: Any) -> CallableComparer:
        return CallableComparer(lambda: self.value >= other)


class AttributesMeta(type):
    def __getattr__(cls, name: str) -> Any | None:
        if name in cls.__annotations__:
            anno = cls.__annotations__[name]
            if issubclass(anno.__origin__, Attribute):
                if isinstance(anno.__metadata__[0], str):
                    return anno.__origin__(anno.__metadata__[0])
                return anno.__metadata__[0]

        raise AttributeError(f"{cls.__name__}  dsafhas no attribute {name}")


class Attributes(metaclass=AttributesMeta):
    def __init__(self, **kwargs: Attribute):
        for name, anno in self.__annotations__.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                setattr(
                    self,
                    name,
                    anno(
                        name,
                    ),
                )
