"""
Dependency injection container for ops engineers.
"""
class Container:
    def __init__(self):
        self._factories = {}
        self._instances = {}

    def register(self, name, factory):
        self._factories[name] = factory

    def resolve(self, name):
        if name in self._instances:
            return self._instances[name]
        if name not in self._factories:
            raise KeyError(name)
        inst = self._factories[name](self)
        self._instances[name] = inst
        return inst