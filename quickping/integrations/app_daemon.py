from typing import Any

import appdaemon.plugins.hass.hassapi as hass  # type: ignore

from quickping import Change, Event, Thing
from quickping.app import QuickpingApp


class AppDaemonApp(hass.Hass):
    quickping: QuickpingApp
    tracked: dict[str, Thing]

    async def initialize(self) -> None:
        self.tracked = {}
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

    def track(self, *things: Thing) -> None:
        for thing in things:
            if thing.id in self.tracked:
                continue

            if not thing.quickping:
                thing.load(self.quickping)

            self.tracked[thing.id] = thing
            if thing.entity:
                thing.entity.listen_state(
                    self.on_state,
                    thing_id=thing.id,
                )
            else:
                print(f"Thing {thing.id} has no entity")

    async def on_state(
        self,
        entity: str,
        attribute: str,
        old: Any,
        new: Any,
        kwargs: dict[str, Any],
    ) -> None:
        change: Change = Change(
            thing_id=kwargs["thing_id"],
            attribute=attribute,
            old=old,
            new=new,
        )

        print(f"State change: {entity}.{attribute} {old} -> {new}")
        await self.quickping.on_change(change)
