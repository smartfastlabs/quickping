from .base import BaseListener as BaseListener
from .change import ChangeListener
from .event import EventListener
from .http import HTTPListener
from .idle import IdleListener
from .scene import SceneListener


def clear() -> None:
    IdleListener.clear()
    ChangeListener.clear()
    EventListener.clear()
    HTTPListener.clear()
    SceneListener.clear()
