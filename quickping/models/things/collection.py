from typing import Any, Optional

from .thing import Thing


class Collection(Thing):
    things: dict[str, Thing]
    instance: Optional["Collection"] = None

    def __init__(self) -> None:
        pass

    def __new__(cls, *args: tuple[Any], **kwargs: dict[str, Any]) -> "Collection":
        if cls.instance is not None:
            return cls.instance

        cls.instance = object.__new__(cls)

        return cls.instance

    @classmethod
    def on_load(cls) -> "Collection":
        if not cls.quickping:
            raise ValueError("QuickpingApp not set on Collection")

        cls.things = {}
        for _key, value in cls.__dict__.items():
            if isinstance(value, Collection | Thing):
                value.load(cls.quickping)
        return cls()

    def get(self, id: str) -> Thing | None:
        return self.things.get(id, None)
