import importlib
import os
import sys
from typing import Any


def fix_name(name: str) -> str:
    return name.split(".")[0].replace("-", "_")


def _import_modules() -> dict[str, Any]:
    from quickping import listeners, models
    from quickping.decorators.collector import Collector

    return {
        "listeners": listeners,
        "Collector": Collector,
        "Thing": models.things.Thing,
    }


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


def load_directory_old(path: str) -> dict[str, Any]:
    modules = _import_modules()
    modules["listeners"].clear()
    modules["Collector"].clear()
    unload_directory(path)

    for root, _, filenames in os.walk(path):
        init_path = os.path.join(root, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w"):
                pass
        for filename in filenames:
            if filename.endswith(".py"):
                module_name = fix_name(filename)
                modules[module_name] = load_file(
                    module_name, os.path.join(root, filename)
                )

    return modules


def load_directory(path: str) -> dict[str, Any]:
    modules = _import_modules()
    modules["listeners"].clear()
    modules["Collector"].clear()
    package_name = os.path.basename(path)
    unload_directory(path)

    init_path = os.path.join(path, "__init__.py")
    if not os.path.exists(path):
        with open(init_path, "w"):
            pass

    spec = importlib.util.spec_from_file_location(  # type: ignore
        package_name,
        init_path,
    )
    package = importlib.util.module_from_spec(spec)  # type: ignore
    sys.modules[package_name] = package
    modules[package_name] = package
    spec.loader.exec_module(package)

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
