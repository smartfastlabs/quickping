def schedule(func):
    def wrapper(*args, **kwargs):
        print(f"Running {func.__name__} with args {args} and kwargs {kwargs}")
        return func(*args, **kwargs)

    return wrapper
