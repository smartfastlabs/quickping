import inspect
from typing import TYPE_CHECKING, List

import appdaemon.plugins.hass.hassapi as hass

if TYPE_CHECKING:
    from listeners import ChangeListener, EventListener, IdleListener, HTTPListener

from .models import Collection, Thing
from .utils.importer import load_directory


def wrap(func, name):
    async def wrapped(*args, **kwargs):
        return await func(*args, **kwargs)

    wrapped.__name__ = name
    return wrapped


class AppDaemonApp(hass.Hass):
    change_listeners: List["ChangeListener"]
    event_listeners: List["EventListener"]
    idle_listeners: List["IdleListener"]
    http_listeners: List["HTTPListener"]
    handler_path: str = "handlers"

    async def initialize(self):
        handlers = load_directory(self.handler_path)
        self.change_listeners = handlers["listeners"].ChangeListener.instances
        self.event_listeners = handlers["listeners"].EventListener.instances
        self.idle_listeners = handlers["listeners"].IdleListener.instances
        self.http_listeners = handlers["listeners"].HTTPListener.instances

        for thing in Thing.instances.values():
            thing.load(self)

        # TODO: Start here....is there any reason to have one event
        # listener and we handle routing...or should we just let AD do it?
        # this becomes even more interesting with whens

        for listener in self.idle_listeners:
            listener.quickping = self
            for thing in listener.things:
                thing.entity.listen_state(
                    wrap(
                        listener.on_change,
                        listener.name,
                    ),
                )

        for listener in self.change_listeners:
            listener.quickping = self
            for thing in listener.things:
                thing.entity.listen_state(
                    wrap(
                        listener.on_change,
                        listener.name,
                    ),
                )

        for listener in self.http_listeners:
            listener.quickping = self
            self.register_endpoint(
                wrap(
                    listener.on_call,
                    listener.name,
                ),
                listener.path,
            )

        self.listen_event(self.on_event)
        self.run_every(self.sweep_idle, "now", 5)

    async def sweep_idle(self, *args, **kwargs):
        for listener in self.idle_listeners:
            if listener.is_active() and listener.is_idle():
                await listener.func(*self.build_args(listener.func))

    async def on_event(self, event: str, entity: dict, *args, **kwargs):
        for listener in self.event_listeners:
            if listener.wants_event(event, entity):
                args = []

                args = self.build_args(
                    listener.func,
                    event=event,
                    entity=entity,
                )

                await listener.func(*args)

    def build_args(self, func, **context):
        sig = inspect.signature(func)
        args = []
        for name, param in sig.parameters.items():
            if isinstance(param._annotation, Thing):
                args.append(param._annotation)
            elif param._annotation and issubclass(param._annotation, Collection):
                args.append(param._annotation())
            elif param.default != param.empty:
                args.append(param.default)
            elif name in context:
                args.append(context[name])
            elif name == "quickping":
                args.append(self)
            else:
                args.append("MISSING")

        return args
