from collections.abc import Callable
from typing import Any

from quickping.utils.clock import get_time


def before(*args: Any, **kwargs: Any) -> Callable:
    t = get_time(*args, **kwargs)

    def decorator(func: Callable) -> Callable:
        func.before = t  # type: ignore
        return func

    return decorator
