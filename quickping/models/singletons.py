class Singleton:
    pass


class SingletonPerId:
    instances: dict[str, "SingletonPerId"]

    def __new__(cls, id: str, *args, **kwargs) -> "SingletonPerId":  # type: ignore
        if not isinstance(id, str):
            raise ValueError("id must be a string")

        if getattr(cls, "instances", None) is None:
            cls.instances = {}

        if id not in cls.instances:
            cls.instances[id] = super().__new__(cls)
            cls.instances[id].__init__(id, *args, **kwargs)  # type: ignore

        return cls.instances[id]
