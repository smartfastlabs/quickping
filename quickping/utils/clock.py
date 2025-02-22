from datetime import time


def get_time(
    first: int | time | None = None,
    am: int | None = None,
    pm: int | None = None,
    minute: int = 0,
) -> time:
    if isinstance(first, time):
        return first
    if isinstance(first, int):
        return time(hour=first, minute=minute)
    if am is not None:
        return time(hour=am, minute=minute)
    if pm is not None:
        return time(hour=pm + 12, minute=minute)

    raise ValueError("Invalid time")
