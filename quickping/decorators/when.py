from quickping import listeners
from quickping.models import Comparer


def when(comparer: Comparer):
    print("123 when comparer", comparer)

    def decorator(func):
        if isinstance(func, listeners.BaseListener):
            func.whens.append(comparer)

        elif hasattr(func, "whens"):
            func.whens.append(comparer)

        else:
            func.whens = [comparer]
        return func

    return decorator
