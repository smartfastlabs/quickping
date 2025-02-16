from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from listeners import ChangeListener, EventListener, HTTPListener, IdleListener

import inspect

from .models import Collection, Thing
from .utils.importer import load_directory


def wrap(func, name):
    async def wrapped(*args, **kwargs):
        return await func(*args, **kwargs)

    wrapped.__name__ = name
    return wrapped


class QuickpingApp:
    change_listeners: List["ChangeListener"]
    event_listeners: List["EventListener"]
    idle_listeners: List["IdleListener"]
    http_listeners: List["HTTPListener"]
    handler_path: str

    def __init__(
        self,
        handler_path: str = "handlers",
        event_listeners=Optional[List["EventListener"]],
        change_listeners=Optional[List["ChangeListener"]],
        idle_listeners=Optional[List["IdleListener"]],
        http_listeners=Optional[List["HTTPListener"]],
    ):
        self.change_listeners = change_listeners
        self.idle_listeners = idle_listeners
        self.http_listeners = http_listeners
        self.event_listeners = event_listeners
        self.handler_path = handler_path

    def load_handlers(self):
        handlers = load_directory(self.handler_path)
        self.change_listeners = handlers["listeners"].ChangeListener.instances
        self.event_listeners = handlers["listeners"].EventListener.instances
        self.idle_listeners = handlers["listeners"].IdleListener.instances
        self.http_listeners = handlers["listeners"].HTTPListener.instances

        for thing in Thing.instances.values():
            thing.load(self)

    def load_listeners(self):
        self.load_idle_listeners()
        self.load_change_listeners()
        self.load_http_listeners()

    def load_idle_listeners(self):
        for listener in self.idle_listeners:
            listener.quickping = self
            for thing in listener.things:
                thing.entity.listen_state(
                    wrap(
                        listener.on_change,
                        listener.name,
                    ),
                )

    def load_change_listeners(self):
        for listener in self.change_listeners:
            listener.quickping = self
            for thing in listener.things:
                thing.entity.listen_state(
                    wrap(
                        listener.on_change,
                        listener.name,
                    ),
                )

    def load_http_listeners(self):
        for listener in self.http_listeners:
            listener.quickping = self
            listener.listen_state(
                wrap(
                    listener.on_change,
                    listener.name,
                ),
            )

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
