class Container:
    """
    Simple DI container.
    """
    def __init__(self):
        self._factories = {}
        self._instances = {}

    def register(self, name, factory):
        self._factories[name] = factory

    def resolve(self, name):
        if name in self._instances:
            return self._instances[name]
        if name in self._factories:
            instance = self._factories[name](self)
            self._instances[name] = instance
            return instance
        raise KeyError(f"No service registered under {name}")
