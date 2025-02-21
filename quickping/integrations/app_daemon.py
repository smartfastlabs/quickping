from typing import Any

import appdaemon.plugins.hass.hassapi as hass  # type: ignore

from quickping import Event
from quickping.app import QuickpingApp


class AppDaemonApp(hass.Hass):
    quickping: QuickpingApp

    async def initialize(self) -> None:
        self.quickping = QuickpingApp(
            self.handler_path,
            app_daemon=self,
        )
        self.quickping.load_handlers()

        self.listen_event(self.on_event)
        self.run_every(self.sweep_idle, "now", 5)

    # TODO: These should all just normalizes the args and call the quickping app
    async def sweep_idle(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> None:
        for listener in self.quickping.idle_listeners:
            if listener.is_active() and listener.is_idle():
                await listener.func(*self.quickping.build_args(listener.func))

    async def on_event(
        self,
        name: str,
        data: dict,
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        event: Event = Event(
            name=name,
            data=data,
        )
        await self.quickping.on_event(event)
