from collections.abc import Callable

from .collector import Collector


def scene(scene_id: str) -> Callable:
    if not scene_id.startswith("scene."):
        scene_id = f"scene.{scene_id}"

    def decorator(func: Callable | Collector) -> Collector:
        if isinstance(func, Collector):
            func.scene_id = scene_id
            return func

        return Collector(
            func,
            scene_id=scene_id,
        )

    return decorator
