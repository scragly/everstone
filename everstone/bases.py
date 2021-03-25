import typing as t


class LimitInstances:
    """Ensures only a single instance exists per name, returning old ones if existing."""

    __instances__: t.Dict[str, object] = dict()

    def __new__(cls, name: str, *args, **kwds):
        """Set the class to a single instance per name."""
        instance = cls.__instances__.get(name)
        if instance is None:
            cls.__instances__[name] = instance = object.__new__(cls)
        return instance
