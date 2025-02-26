from collections.abc import Callable

from .collector import Collector


def route(route: str) -> Callable:
    def decorator(func: Callable | Collector) -> Collector:
        if isinstance(func, Collector):
            func.route = route
            return func

        return Collector(
            func,
            route=route,
        )

    return decorator
