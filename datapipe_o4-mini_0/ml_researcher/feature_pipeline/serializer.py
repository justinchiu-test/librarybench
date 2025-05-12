class SerializerRegistry:
    def __init__(self):
        self._handlers = {}

    def register(self, fmt, handler):
        self._handlers[fmt] = handler

    def serialize(self, fmt, data, *args, **kwargs):
        if fmt not in self._handlers:
            raise ValueError(f"No serializer registered for format: {fmt}")
        return self._handlers[fmt](data, *args, **kwargs)

# module-level registry
registry = SerializerRegistry()
