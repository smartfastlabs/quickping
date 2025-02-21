from collections.abc import Callable

from quickping import listeners
from quickping.utils.comparer import Comparer


def when(*comparers: Comparer) -> Callable:
    def decorator(
        func: Callable | listeners.ChangeListener,
    ) -> listeners.ChangeListener:
        comparer = comparers[0]
        if len(comparers) > 1:
            for c in comparers[1:]:
                comparer = comparer & c
        if isinstance(func, listeners.ChangeListener):
            return func.add_when(comparer)

        return listeners.ChangeListener(
            name=f"{func.__module__}.{func.__name__}",
            func=func,
            whens=[comparer],
        )

    return decorator
