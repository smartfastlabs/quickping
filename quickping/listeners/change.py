from quickping.models import Change, Thing

from .base import BaseListener


class ChangeListener(BaseListener):
    things: list[Thing] | None = None

    async def on_change(
        self,
        thing_id: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: dict,
    ) -> None:
        if not self.is_active():
            return

        change = Change(
            thing_id=thing_id,
            attribute=attribute,
            old=old,
            new=new,
        )
        args = self.quickping.build_args(
            self.func,
            change=change,
        )
        await self.func(*args)
