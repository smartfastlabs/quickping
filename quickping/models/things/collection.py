from typing import Any, Optional

from .thing import Thing


class CollectionMeta(type):
    def __getattr__(cls, name: str) -> Any | None:
        if name in cls.__annotations__:
            anno = cls.__annotations__[name]
            if not hasattr(anno, "__origin__"):
                return anno()
            elif issubclass(anno.__origin__, Thing):
                if isinstance(anno.__metadata__[0], str):
                    return anno.__origin__(anno.__metadata__[0])
                return anno.__metadata__[0]

        raise AttributeError(f"{cls.__name__} has no attribute {name}")


class Collection(Thing):
    things: dict[str, Thing]
    instance: Optional["Collection"] = None

    def __init__(
        self,
        _id: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if _id is None:
            _id = f"{self.__module__}.{self.__class__.__name__}"

        super().__init__(_id, *args, **kwargs)

    def __new__(cls) -> "Collection":
        if cls.instance is not None:
            return cls.instance

        _id: str = f"{cls.__module__}.{cls.__name__}"

        cls.instance = super().__new__(cls, _id)  # type: ignore
        if cls.instance is not None:
            cls.instance.things = {}  # type: ignore
            return cls.instance

        raise ValueError("Could not create instance of Collection")

    def on_load(self) -> "Collection":
        if not self.quickping:
            raise ValueError("QuickpingApp not set on Collection")

        for key, anno in self.__annotations__.items():
            thing: Thing | None = None
            if not hasattr(anno, "__origin__"):
                if not getattr(self, key):
                    setattr(self, key, anno)
            elif issubclass(anno.__origin__, Thing):
                if isinstance(anno.__metadata__[0], str):
                    thing = anno.__origin__(anno.__metadata__[0])
                else:
                    thing = anno.__metadata__[0]

            if thing is not None:
                setattr(self, key, thing)
                self.things[key] = thing

        self.things = {}
        for _key, value in self.__dict__.items():
            if isinstance(value, Collection | Thing):
                value.load(self.quickping)
        return self
