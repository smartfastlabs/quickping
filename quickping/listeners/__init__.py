from .change import ChangeListener
from .event import EventListener
from .http import HTTPListener
from .idle import IdleListener


def clear() -> None:
    IdleListener.clear()
    ChangeListener.clear()
    EventListener.clear()
    HTTPListener.clear()
