from collections.abc import Callable

from quickping.models import Comparer


def when(comparer: Comparer) -> Callable:
    print("123 when comparer", comparer)

    def decorator(func: Callable) -> Callable:
        if hasattr(func, "whens"):
            func.whens.append(comparer)

        else:
            func.whens = [comparer]  # type: ignore
        return func

    return decorator
