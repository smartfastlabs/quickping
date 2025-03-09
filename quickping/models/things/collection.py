import asyncio
from typing import Any, Optional

from quickping.utils.comparer import AndComparer, Comparer

from .thing import Thing


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
        # TODO: cleanup, document, understand
        if not self.quickping:
            raise ValueError("QuickpingApp not set on Collection")

        for key, anno in self.__annotations__.items():
            if key == "state":
                continue
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

        temp: dict[str, Any] = {}
        for key, value in self.__class__.__dict__.items():
            if key == "instance":
                continue
            if isinstance(value, Thing):
                temp[key] = value

        for key, value in self.__dict__.items():
            if isinstance(value, Collection | Thing):
                temp[key] = value

        for _key, value in temp.items():
            if isinstance(value, Collection | Thing):
                value.load(self.quickping)
                self.things[_key] = value
        return self

    def all_things(self) -> list[Thing]:
        things: dict[str, Thing] = {}
        for thing in self.things.values():
            if isinstance(thing, Collection):
                for subthing in thing.all_things():
                    things[thing.id] = subthing
            else:
                things[thing.id] = thing
        return list(things.values())

    async def turn_on(self, *args: Any, **kwargs: Any) -> None:
        await asyncio.gather(*(t.turn_on(*args, **kwargs) for t in self.all_things()))

    async def turn_off(self, *args: Any, **kwargs: Any) -> None:
        await asyncio.gather(*(t.turn_off(*args, **kwargs) for t in self.all_things()))

    @property
    def is_on(self) -> Comparer:
        return AndComparer(
            comparers=[t.is_on for t in self.all_things()],
        )

    @property
    def is_off(self) -> Comparer:
        return AndComparer(
            comparers=[t.is_off for t in self.all_things()],
        )
