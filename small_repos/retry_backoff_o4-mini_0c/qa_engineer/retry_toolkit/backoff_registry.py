class BackoffRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, name, func):
        self._registry[name] = func

    def get(self, name):
        return self._registry.get(name)
