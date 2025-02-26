from inspect import isclass


class AttributesMeta(type):
    def __new__(cls, class_name, bases, attrs):  # type: ignore
        if "__annotations__" in attrs:
            for name, anno in list(attrs["__annotations__"].items()):
                if name == "state":
                    continue
                if name in attrs:
                    continue
                if not hasattr(anno, "__origin__"):
                    if isclass(anno):
                        attrs[name] = anno()
                    else:
                        attrs[name] = anno
                elif isclass(anno.__origin__) and hasattr(anno, "__metadata__"):
                    if isinstance(anno.__metadata__[0], anno.__origin__):
                        attrs[name] = anno.__metadata__[0]
                    else:
                        attrs[name] = anno.__origin__(anno.__metadata__[0])

                if name == "lights":
                    print("META", attrs[name].id)
        return super().__new__(cls, class_name, bases, attrs)
