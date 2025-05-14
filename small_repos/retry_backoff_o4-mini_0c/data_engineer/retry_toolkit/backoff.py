class BackoffRegistry:
    _registry = {}

    @classmethod
    def register(cls, name, func):
        cls._registry[name] = func

    @classmethod
    def get(cls, name):
        return cls._registry[name]
