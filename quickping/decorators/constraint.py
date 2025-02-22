from collections.abc import Callable
from datetime import time


def constraint(
    before: time | None = None,
    after: time | None = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        if before is not None:
            func.before = before  # type: ignore
        if after is not None:
            func.after = after  # type: ignore
        return func

    return decorator
