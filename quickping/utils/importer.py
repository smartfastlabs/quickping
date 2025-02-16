import importlib
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from quickping import listeners


def fix_name(name: str) -> str:
    return name.split(".")[0].replace("-", "_")


def unload_directory(path: str, ignore: List[str] = []):
    for name, module in list(sys.modules.items()):
        if (
            module
            and name not in ignore
            and hasattr(module, "__file__")
            and module.__file__
            and module.__file__.startswith(path)
        ):
            if name in sys.modules:
                del sys.modules[name]


def load_directory(path: str) -> Dict[str, Any]:
    modules = {
        "listeners": listeners,
    }
    listeners.clear()
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
    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
