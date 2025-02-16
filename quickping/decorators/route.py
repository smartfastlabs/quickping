from quickping import listeners


def route(path: str):
    def decorator(func):
        return listeners.HTTPListener(
            name=f"{func.__module__}.{func.__name__}",
            path=path,
            func=func,
        )

    return decorator
