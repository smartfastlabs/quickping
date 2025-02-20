from inspect import isclass
from typing import Any


class AttributesMeta(type):
    def __getattr__(cls, name: str) -> Any | None:
        if name in cls.__annotations__:
            anno = cls.__annotations__[name]
            if not hasattr(anno, "__origin__"):
                return anno()
            elif isclass(anno.__origin__):
                if isinstance(anno.__metadata__[0], str):
                    return anno.__origin__(anno.__metadata__[0])
                return anno.__metadata__[0]

        raise AttributeError(f"{cls.__name__} has no attribute {name}")
