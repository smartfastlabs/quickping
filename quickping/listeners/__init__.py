from .base import BaseListener as BaseListener
from .change import ChangeListener
from .event import EventListener
from .http import HTTPListener
from .idle import IdleListener
from .scene import SceneListener
from .schedule import ScheduleListener


def clear() -> None:
    IdleListener.clear()
    ChangeListener.clear()
    EventListener.clear()
    HTTPListener.clear()
    ScheduleListener.clear()
    SceneListener.clear()
