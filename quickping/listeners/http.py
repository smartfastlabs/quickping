from typing import Any

from .base import BaseListener


class HTTPListener(BaseListener):
    path: str

    async def on_call(self, request: dict, cb_args: dict) -> tuple[Any, int]:
        args = self.quickping.build_args(self.func, request=request)

        result = await self.func(*args)
        if isinstance(result, tuple):
            return result
        return result, 200
