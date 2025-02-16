import asyncio
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from quickping.app import AppDaemonApp

from .thing import Thing


class Collection(Thing):
    things: Dict[str, Thing]
    instance: "Collection" = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if cls.instance is not None:
            return cls.instance

        id = f"collection.{cls.__module__.lower()}.{cls.__name__.lower()}"
        cls.instance = object.__new__(cls)

        return cls.instance

    @classmethod
    def on_load(cls) -> "Collection":
        cls.things = {}
        for key, value in cls.__dict__.items():
            if isinstance(value, (Collection, Thing)):
                value.load(cls.quickping)
        return cls()

    def for_each(self, name, *args, **kwargs) -> List:
        results: List = []
        for thing in self.things.values():
            results.append(getattr(thing, name)(*args, **kwargs))

        return results

    async def for_each_async(self, name, *args, **kwargs):
        return await asyncio.gather(
            getattr(thing, name)(*args, **kwargs)
            for thing in self.things.values()
            if hasattr(thing, name)
        )

    def all(cls, *thing_types: Tuple[type]) -> List[Thing]:
        if not thing_types:
            return list(cls.things.values())

        return [
            thing
            for thing in cls.things.values()
            if isinstance(thing, tuple(thing_types))
        ]

    def get(self, id: str) -> Optional[Thing]:
        return self.things.get(id, None)
