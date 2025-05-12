"""
Dependency injection for translator.
"""
class DependencyInjector:
    def __init__(self):
        self._deps = {}

    def register(self, name, instance):
        self._deps[name] = instance

    def resolve(self, name):
        if name not in self._deps:
            raise KeyError(name)
        return self._deps[name]