class Singleton:
    pass


class SingletonPerId:
    instances: dict[str, "TrackInstances"]

    def __new__(cls, id, *args, **kwargs):
        if not hasattr(cls, "instances"):
            cls.instances = {}

        if id not in cls.instances:
            cls.instances[id] = super().__new__(cls)
            cls.instances[id].__init__(id, *args, **kwargs)

        return cls.instances[id]
