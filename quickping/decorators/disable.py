from collections.abc import Callable

from .collector import Collector


def disable(func: Callable | Collector) -> Collector:
    if isinstance(func, Collector):
        func.disabled = True
        return func

    return Collector(func, disabled=True)
