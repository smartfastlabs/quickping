from collections.abc import Callable

from quickping import listeners


def route(path: str) -> Callable:
    def decorator(func: Callable) -> listeners.HTTPListener:
        return listeners.HTTPListener(
            name=f"{func.__module__}.{func.__name__}",
            path=path,
            func=func,
        )

    return decorator
