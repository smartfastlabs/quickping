from collections import defaultdict
from typing import List

from .base import BaseListener
from .change import ChangeListener
from .event import EventListener
from .http import HTTPListener
from .idle import IdleListener

_LISTENER_INDEX = defaultdict(list)


def clear():
    IdleListener.clear()
    ChangeListener.clear()
    EventListener.clear()
    HTTPListener.clear()


def get_listeners(thing_id: str) -> List:
    return _LISTENER_INDEX.get(thing_id, [])


def build_index():
    for listener in ChangeListener.instances + IdleListener.instances:
        for thing in listener.things:
            _LISTENER_INDEX[thing.id].append(listener)
    return _LISTENER_INDEX
