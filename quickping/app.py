import asyncio
from collections.abc import Callable
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
    ScheduleListener,
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
    schedule_listeners: list["ScheduleListener"]
    scene_listeners: list["SceneListener"]
    listeners: list[
        EventListener
        | HTTPListener
        | IdleListener
        | ChangeListener
        | ScheduleListener
        | SceneListener
    ]
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
        schedule_listeners: list["ScheduleListener"] | None = None,
        scene_listeners: list["SceneListener"] | None = None,
        app_daemon: Optional["Hass"] = None,
    ):
        self.change_listeners = change_listeners or []
        self.idle_listeners = idle_listeners or []
        self.http_listeners = http_listeners or []
        self.event_listeners = event_listeners or []
        self.schedule_listeners = schedule_listeners or []
        self.scene_listeners = scene_listeners or []
        self.listeners = (
            self.change_listeners
            + self.idle_listeners
            + self.http_listeners
            + self.event_listeners
            + self.schedule_listeners
            + self.scene_listeners
        )
        self.handler_path = handler_path
        self.faux_things = []
        self.app_daemon = app_daemon

    async def load_handlers(self) -> None:
        modules: dict = load_directory(self.handler_path)

        for thing in list(Thing.instances.values()):
            if hasattr(thing, "load"):
                thing.load(self)

        for collector in modules["Collector"].instances:
            if collector.disabled:
                continue

            listener_args = collector.get_listener_args()
            listeners: list[
                EventListener
                | HTTPListener
                | IdleListener
                | ChangeListener
                | ScheduleListener
                | SceneListener
            ] = []

            if things := collector.all_things():
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
                self.app_daemon.track(*things)  # type: ignore
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
                        await self.app_daemon.call_service(
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

            if collector.run_on_interval is not None or collector.run_at:
                schedule_listener: ScheduleListener = ScheduleListener(
                    quickping=self,
                    **listener_args,
                )
                self.schedule_listeners.append(schedule_listener)
                listeners.append(schedule_listener)

            self.listeners.extend(listeners)

        self.faux_things: list[type[FauxThing]] = get_all_subclasses(FauxThing)
        for faux_thing in self.faux_things:
            faux_thing.start(self)  # type: ignore

    async def on_change(self, change: Change) -> None:
        self._track_state_change(change)
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

    def _track_state_change(self, change: Change) -> None:
        if change.thing_id not in Thing.instances:
            return

        thing: Thing = Thing.instances[change.thing_id]
        attr: Any = getattr(thing, change.attribute, None)
        if attr and isinstance(attr, ValueComparer):
            attr.value = change.new
            return
        thing.properties[change.attribute] = change.new

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

                for schedule_listener in self.schedule_listeners:
                    if schedule_listener.is_triggered():
                        futures.append(
                            schedule_listener.run(
                                *self.build_args(
                                    schedule_listener.func,
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
