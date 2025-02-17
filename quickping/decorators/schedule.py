from collections.abc import Callable


def schedule(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):  # type: ignore
        print(f"Running {func.__name__} with args {args} and kwargs {kwargs}")
        return func(*args, **kwargs)

    return wrapper
