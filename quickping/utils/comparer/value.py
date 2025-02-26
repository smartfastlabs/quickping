from typing import TYPE_CHECKING, Any, Optional

from .callable import CallableComparer

if TYPE_CHECKING:
    from quickping.models.things.thing import Thing


class ValueComparer:
    entity: Any
    thing: Optional["Thing"]
    name: str
    value_type: type | None = None

    def __init__(
        self,
        name: str,
        entity: Any = None,
        thing: Optional["Thing"] = None,
        value_type: type | None = None,
    ):
        self.value_type = value_type
        self.entity = entity
        self.name = name
        self.thing = thing

    def things(self) -> list["Thing"]:
        if not self.thing:
            print("NO THING")
            return []

        return [self.thing]

    @property
    def value(self) -> Any:
        if self.entity:
            # TODO HORRIBLE HACK This was necessary when supporting _state on things
            entity_name: str = self.name.lstrip("_")
            if hasattr(self.entity, "attributes") and hasattr(
                self.entity.attributes,
                entity_name,
            ):
                return getattr(
                    self.entity.attributes,
                    entity_name,
                    None,
                )

            if hasattr(self.entity, entity_name):
                return getattr(
                    self.entity,
                    entity_name,
                    None,
                )

        return getattr(
            self.thing,
            self.name,
            None,
        )

    def __eq__(self, other: Any) -> CallableComparer:  # type: ignore
        return CallableComparer(
            lambda: self.value == other,
            things=self.things,
        )

    def __lt__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value < other,
            things=self.things,
        )

    def __le__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value <= other,
            things=self.things,
        )

    def __gt__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value > other,
            things=self.things,
        )

    def __ge__(self, other: Any) -> CallableComparer:
        return CallableComparer(
            lambda: self.value >= other,
            things=self.things,
        )
