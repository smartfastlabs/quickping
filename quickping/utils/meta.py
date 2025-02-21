from inspect import isclass


class AttributesMeta(type):
    def __new__(cls, name, bases, attrs):  # type: ignore
        if "__annotations__" in attrs:
            for name, anno in list(attrs["__annotations__"].items()):
                if name in attrs:
                    continue
                if name == "light":
                    print("HERE", name, anno)
                if not hasattr(anno, "__origin__"):
                    attrs[name] = anno()
                elif isclass(anno.__origin__) and hasattr(anno, "__metadata__"):
                    _id = anno.__metadata__[0]
                    if hasattr(_id, "id"):
                        _id = _id.id
                    attrs[name] = anno.__origin__(_id)

        return super().__new__(cls, name, bases, attrs)
