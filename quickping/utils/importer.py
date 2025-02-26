import importlib
import os
import sys
from typing import Any

from quickping import listeners
from quickping.decorators.collector import Collector


def fix_name(name: str) -> str:
    return name.split(".")[0].replace("-", "_")


def unload_directory(
    path: str,
    ignore: list[str] | None = None,
) -> None:
    if ignore is None:
        ignore = []
    for name, module in list(sys.modules.items()):
        if (
            module
            and name not in ignore
            and hasattr(module, "__file__")
            and module.__file__
            and module.__file__.startswith(path)
        ) and name in sys.modules:
            del sys.modules[name]


def load_directory(path: str) -> dict[str, Any]:
    modules = {
        "listeners": listeners,
        "Collector": Collector,
    }
    listeners.clear()
    Collector.clear()
    unload_directory(path)

    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".py"):
                module_name = fix_name(filename)
                modules[module_name] = load_file(
                    module_name, os.path.join(root, filename)
                )

    return modules


def load_file(module_name: str, path: str) -> Any:
    spec = importlib.util.spec_from_file_location(  # type: ignore
        module_name,
        path,
    )
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)
    return module


def get_all_subclasses(cls: type) -> list[type]:
    all_subclasses: list[type] = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses
