import inspect
from typing import TYPE_CHECKING, List

import appdaemon.plugins.hass.hassapi as hass

if TYPE_CHECKING:
    from listeners import ChangeListener, EventListener, IdleListener, HTTPListener

from ..app import QuickpingApp
from ..models import Collection, Thing
from ..utils.importer import load_directory


class AppDaemonApp(hass.Hass):
    quickping: QuickpingApp

    async def initialize(self):
        self.quickping = QuickpingApp(self.handler_path)
        self.quickping.load_handlers()

        self.listen_event(self.on_event)
        self.run_every(self.sweep_idle, "now", 5)

    # TODO: These should all just normalizes the args and call the quickping app
    async def sweep_idle(self, *args, **kwargs):
        for listener in self.quickping.idle_listeners:
            if listener.is_active() and listener.is_idle():
                await listener.func(*self.quickping.build_args(listener.func))

    async def on_event(self, event: str, entity: dict, *args, **kwargs):
        for listener in self.quickping.event_listeners:
            if listener.wants_event(event, entity):
                args = []

                args = self.quickping.build_args(
                    listener.func,
                    event=event,
                    entity=entity,
                )

                await listener.func(*args)
