from collections.abc import Callable

from quickping import listeners
from quickping.models import Comparer


def when(comparer: Comparer) -> Callable:
    def decorator(
        func: Callable | listeners.ChangeListener,
    ) -> listeners.ChangeListener:
        if isinstance(func, listeners.ChangeListener):
            return func.add_when(comparer)

        return listeners.ChangeListener(
            name=f"{func.__module__}.{func.__name__}",
            func=func,
            whens=[comparer],
        )

    return decorator
