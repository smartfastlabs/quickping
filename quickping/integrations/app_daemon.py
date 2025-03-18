import asyncio
import pathlib
from inspect import getfile
from typing import Any

import appdaemon.plugins.hass.hassapi as hass  # type: ignore

from quickping import Change, Event, FauxThing, Thing
from quickping.app import QuickpingApp


class AppDaemonApp(hass.Hass):
    quickping: QuickpingApp
    tracked: dict[str, Thing]
    quickping_task: asyncio.Task | None

    handler_path: str | None

    async def initialize(self) -> None:
        self.tracked = {}
        self.quickping = QuickpingApp(
            app_daemon=self,
        )
        await self.quickping.load_handlers(
            getattr(
                self,
                "handler_path",
                pathlib.Path(
                    getfile(self.__class__),
                ).parent.resolve()
                / "home",
            )
        )
        self.listen_event(self.on_event)
        self.quickping_task = asyncio.create_task(self.quickping.run())

    async def terminate(self) -> None:
        if qp := getattr(self, "quickping_task", None):
            qp.cancel()
            try:
                await qp
            except asyncio.CancelledError:
                print("Quickping task cancelled")
        if quickping := getattr(self, "quickping", None):
            await quickping.terminate()

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

            if isinstance(thing, FauxThing) or not isinstance(thing, Thing):
                continue

            self.tracked[thing.id] = thing
            entity = self.get_entity(thing.id)
            if entity:
                print("TRACKING", thing.id)
                entity.listen_state(
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

        await self.quickping.on_change(change)
