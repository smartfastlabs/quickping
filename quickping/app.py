import asyncio
import pathlib
from collections.abc import Callable, Generator
from contextlib import contextmanager
from inspect import isclass
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    try:
        from appdaemon.entity import Entity  # type: ignore
        from appdaemon.plugins.hass.hassapi import Hass  # type: ignore
    except ImportError:
        Hass = None
        Entity = None

import inspect

from .listeners import (
    ChangeListener,
    EventListener,
    HTTPListener,
    IdleListener,
    SceneListener,
)
from .models import Change, Collection, Event, FauxThing, Thing
from .utils.comparer import ValueComparer
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
    scene_listeners: list["SceneListener"]
    listeners: list[
        EventListener | HTTPListener | IdleListener | ChangeListener | SceneListener
    ]
    faux_things: list[FauxThing]
    things: list[Thing]
    app_daemon: Optional["Hass"]
    handlers: dict[str, Any]

    def __init__(
        self,
        event_listeners: list["EventListener"] | None = None,
        change_listeners: list["ChangeListener"] | None = None,
        idle_listeners: list["IdleListener"] | None = None,
        http_listeners: list["HTTPListener"] | None = None,
        scene_listeners: list["SceneListener"] | None = None,
        app_daemon: Optional["Hass"] = None,
    ):
        self.handlers = {}
        self.change_listeners = change_listeners or []
        self.idle_listeners = idle_listeners or []
        self.http_listeners = http_listeners or []
        self.event_listeners = event_listeners or []
        self.scene_listeners = scene_listeners or []
        self.listeners = (
            self.change_listeners
            + self.idle_listeners
            + self.http_listeners
            + self.event_listeners
            + self.scene_listeners
        )
        self.faux_things = []
        self.things = []
        self.app_daemon = app_daemon

    async def load_handlers(self, path: str | pathlib.Path) -> None:
        self.handlers = load_directory(str(path))

        for thing in list(self.handlers["Thing"].instances.values()):
            if hasattr(thing, "load"):
                thing.load(self)

            if isinstance(thing, (FauxThing, Collection)):
                continue

            domain, is_valid = thing.id.split(".", 1)
            if is_valid:
                self.things.append(thing)
        self.app_daemon.track(*self.things)  # type: ignore

        for collector in self.handlers["Collector"].instances:
            if collector.disabled:
                continue

            listener_args = collector.get_listener_args()
            listeners: list[
                EventListener
                | HTTPListener
                | IdleListener
                | ChangeListener
                | SceneListener
            ] = []

            if collector.all_things():
                listener: ChangeListener | IdleListener
                if collector.idle_time is not None:
                    listener = IdleListener(
                        quickping=self,
                        **listener_args,
                    )
                    self.idle_listeners.append(listener)
                else:
                    listener = ChangeListener(
                        quickping=self,
                        **listener_args,
                    )
                    self.change_listeners.append(listener)

                listeners.append(listener)

            if collector.event_filter or collector.event_payload_filter:
                event_listener: EventListener = EventListener(
                    quickping=self,
                    **listener_args,
                )
                self.event_listeners.append(event_listener)
                listeners.append(event_listener)

            if collector.scene_id:
                scene_listener: SceneListener = SceneListener(
                    quickping=self,
                    **listener_args,
                )
                if self.app_daemon:
                    if not self.get_entity(collector.scene_id):
                        print("Creating scene", collector.scene_id)
                        await self.call_service(
                            "scene/create",
                            scene_id=collector.scene_id.split("scene.", 1)[-1],
                            entities={collector.scene_id: "on"},
                            return_result=True,
                        )
                    else:
                        print("Scene exists", collector.scene_id)
                self.scene_listeners.append(scene_listener)
                self.listeners.append(scene_listener)

            if collector.route:
                http_listener: HTTPListener = HTTPListener(
                    quickping=self,
                    **listener_args,
                )
                self.http_listeners.append(http_listener)
                listeners.append(http_listener)

            self.listeners.extend(listeners)

        self.faux_things = get_all_subclasses(FauxThing)  # type: ignore
        for faux_thing in self.faux_things:
            faux_thing.start(self)

    async def terminate(self) -> None:
        print("Terminating QuickpingApp")
        for thing in self.faux_things:
            print("Stopping faux thing", thing.__class__.__name__)
            thing.stop()

    async def on_change(self, change: Change) -> None:
        with self._track_state_change(change):
            futures = []
            for listener in self.change_listeners:
                if listener.wants_change(change):
                    futures.append(
                        listener.run(
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

    @contextmanager
    def _track_state_change(self, change: Change) -> Generator[Thing]:
        thing: Thing | None = self.get_thing(change.thing_id)
        if not thing:
            print(f"Thing {change.thing_id} not found")
            return

        attr: Any = getattr(thing, change.attribute, None)
        if change.thing_id == "cover.office_blind_cover":
            print("Cover change", change, attr)
        if attr and isinstance(attr, ValueComparer):
            attr.set_value(change.new)
        elif hasattr(thing, "properties"):
            thing.properties[change.attribute] = change.new

        try:
            yield thing
        finally:
            if attr and isinstance(attr, ValueComparer):
                attr.commit()

    async def run(self) -> None:
        try:
            while True:
                futures = []
                for idle_listener in self.idle_listeners:
                    if idle_listener.is_idle():
                        futures.append(
                            idle_listener.run(
                                *self.build_args(
                                    idle_listener.func,
                                )
                            )
                        )

                try:
                    await asyncio.gather(asyncio.sleep(0.5), *futures)
                except Exception as e:
                    print(f"Error running idle listeners: {e}")
        except Exception as e:
            print(f"Error running QuickpingApp {e}")
            await self.run()

    async def on_event(self, event: Event) -> None:
        futures = []
        for listener in self.event_listeners:
            if listener.wants_event(event):
                futures.append(
                    listener.run(
                        *self.build_args(
                            listener.func,
                            event=event,
                        ),
                    ),
                )

        if (
            event.name == "call_service"
            and event.data["domain"] == "scene"
            and event.data["service"] == "turn_on"
        ):
            for scene_listener in self.scene_listeners:
                if scene_listener.wants_event(event):
                    futures.append(
                        scene_listener.run(
                            *self.build_args(
                                scene_listener.func,
                                event=event,
                            ),
                        ),
                    )

        await asyncio.gather(*futures)

    async def call_service(
        self,
        service: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if not self.app_daemon:
            return

        await self.app_daemon.call_service(
            service,
            *args,
            **kwargs,
        )

    async def call_thing_service(
        self,
        service: str,
        thing_id: str,
        **kwargs: Any,
    ) -> None:
        if not self.app_daemon:
            return

        entity: Optional["Entity"] = self.get_entity(thing_id)
        if not entity:
            print(f"Entity {thing_id} not found")
            return

        await entity.call_service(service, **kwargs)

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
            elif name in ("quickping", "qp", "app"):
                args.append(self)
            elif name in ("app_daemon", "hass", "appdaemon"):
                if not self.app_daemon:
                    raise ValueError("AppDaemon not set on QuickpingApp")
                args.append(self.app_daemon)
            else:
                raise ValueError(f"Missing argument {name} for {func}")

        return args

    def get_entity(self, entity_id: str) -> Optional["Entity"]:
        if not self.app_daemon:
            return None

        if type(entity_id) is not str:
            raise ValueError(f"Entity ID must be a string, got {type(entity_id)}")

        print("Getting entity", entity_id)
        return self.app_daemon.get_entity(entity_id)

    def get_thing(self, thing_id: str) -> Thing | None:
        return self.handlers["Thing"].get(thing_id)  # type: ignore
