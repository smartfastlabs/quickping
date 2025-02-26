from collections.abc import Callable
from typing import Any

from quickping.utils.clock import get_time

from .collector import Collector


def before(*args: Any, **kwargs: Any) -> Callable:
    t = get_time(*args, **kwargs)

    def decorator(func: Callable | Collector) -> Collector:
        if isinstance(func, Collector):
            func.before_time = t
            return func

        return Collector(func, before_time=t)

    return decorator
