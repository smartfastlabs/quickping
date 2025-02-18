import importlib
import os

from . import app, decorators, models
from .app import QuickpingApp as QuickpingApp
from .models import (
    Change as Change,
    Collection as Collection,
    Device as Device,
    SensorValue as SensorValue,
    Thing as Thing,
)
from .utils import importer


def load():
    for module in [app, decorators, models, importer]:
        importlib.reload(module)


def reload():
    path = os.path.dirname(os.path.abspath(__file__))
    importer.unload_directory(path, ignore=["app"])


load()
