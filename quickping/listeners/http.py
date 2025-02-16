from .base import BaseListener


class HTTPListener(BaseListener):
    path: str

    async def on_call(self, request: dict, cb_args: dict):
        args = self.quickping.build_args(self.func, request=request)

        result = await self.func(*args)
        if len(result) == 2:
            return result
        return result, 200
