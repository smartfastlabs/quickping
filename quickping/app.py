import asyncio
from collections.abc import Callable
from inspect import isclass
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .listeners import ChangeListener, EventListener, HTTPListener, IdleListener

    try:
        from appdaemon.entity import Entity  # type: ignore
        from appdaemon.plugins.hass.hassapi import Hass  # type: ignore
    except ImportError:
        Hass = None
        Entity = None

import inspect

from .models import Change, Collection, Event, FauxThing, Thing
from .utils.importer import get_all_subclasses, load_directory


def wrap(func: Callable, name: str) -> Callable:
    # TODO Figure out why this is needed
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        return await func(*args, **kwargs)

    wrapped.__name__ = name
    return wrapped


class QuickpingApp:
    change_listeners: list["ChangeListener"]
    event_listeners: list["EventListener"]
    idle_listeners: list["IdleListener"]
    http_listeners: list["HTTPListener"]
    faux_things: list[type]
    handler_path: str
    app_daemon: Optional["Hass"]

    def __init__(
        self,
        handler_path: str = "handlers",
        event_listeners: list["EventListener"] | None = None,
        change_listeners: list["ChangeListener"] | None = None,
        idle_listeners: list["IdleListener"] | None = None,
        http_listeners: list["HTTPListener"] | None = None,
        app_daemon: Optional["Hass"] = None,
    ):
        self.change_listeners = change_listeners or []
        self.idle_listeners = idle_listeners or []
        self.http_listeners = http_listeners or []
        self.event_listeners = event_listeners or []
        self.handler_path = handler_path
        self.faux_things = []
        self.app_daemon = app_daemon

    def load_handlers(self) -> None:
        handlers = load_directory(self.handler_path)
        self.change_listeners = handlers["listeners"].ChangeListener.instances
        self.event_listeners = handlers["listeners"].EventListener.instances
        self.idle_listeners = handlers["listeners"].IdleListener.instances
        self.http_listeners = handlers["listeners"].HTTPListener.instances

        for thing in list(Thing.instances.values()):
            if hasattr(thing, "load"):
                thing.load(self)

        for listener in self.idle_listeners + self.change_listeners:
            listener.quickping = self
            if self.app_daemon:
                self.app_daemon.track(*listener.things)

        for http_listener in self.http_listeners:
            http_listener.quickping = self

        self.faux_things = get_all_subclasses(FauxThing)
        for faux_thing in self.faux_things:
            faux_thing().start(self)

    async def on_change(self, change: Change) -> None:
        futures = []
        for listener in self.change_listeners:
            if listener.wants_change(change):
                futures.append(
                    listener.func(
                        *self.build_args(
                            listener.func,
                            change=change,
                        )
                    )
                )

        for idle_listener in self.idle_listeners:
            if idle_listener.change_applies(change):
                futures.append(idle_listener.on_change())

        await asyncio.gather(*futures)

    async def on_event(self, event: Event) -> None:
        futures = []
        for listener in self.event_listeners:
            if listener.wants_event(event):
                futures.append(
                    listener.func(
                        *self.build_args(
                            listener.func,
                            event=event,
                        ),
                    ),
                )

        await asyncio.gather(*futures)

    def build_args(self, func: Callable, **context: Any) -> list[Any]:
        sig = inspect.signature(func)
        args: list[Any] = []
        for name, param in sig.parameters.items():
            if param.default != param.empty:
                if isclass(param.default) and issubclass(
                    param.default,
                    Collection,
                ):
                    collection = param.default()
                    if collection.quickping is None:
                        collection.load(self)
                    args.append(collection)
                else:
                    args.append(param.default)
            elif isinstance(param.annotation, Thing):
                args.append(param.annotation)
            elif isclass(param.annotation) and issubclass(
                param.annotation,
                Collection,
            ):
                collection = param.annotation()
                if collection.quickping is None:
                    collection.load(self)
                args.append(collection)
            elif name in context:
                args.append(context[name])
            elif name == "quickping":
                args.append(self)
            else:
                args.append("MISSING")

        return args

    def get_entity(self, entity_id: str) -> Optional["Entity"]:
        if not self.app_daemon:
            return None

        if type(entity_id) is not str:
            raise ValueError(f"Entity ID must be a string, got {type(entity_id)}")

        return self.app_daemon.get_entity(entity_id)

    def get_thing(self, thing_id: str) -> Thing | None:
        return Thing.get(thing_id)
