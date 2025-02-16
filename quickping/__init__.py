import importlib
import os

from .app import QuickpingApp
from .decorators import on_change, on_event, on_idle, route, when
from .integrations.app_daemon import AppDaemonApp
from .models import Change, Collection, Comparer, Device, SensorValue, Thing
from .utils import importer


def load():
    for module in [app, decorators, models, importer]:
        importlib.reload(module)


def reload():
    path = os.path.dirname(os.path.abspath(__file__))
    importer.unload_directory(path, ignore=["app"])


load()
