from collections.abc import Callable


def disable(func: Callable) -> Callable:
    func.disabled = True  # type: ignore
    return func
