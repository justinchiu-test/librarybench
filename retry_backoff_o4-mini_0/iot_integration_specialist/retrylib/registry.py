class BackoffRegistry:
    _registry = {}

    @classmethod
    def register(cls, name, strategy_cls):
        cls._registry[name] = strategy_cls

    @classmethod
    def get(cls, name):
        if name not in cls._registry:
            raise KeyError(f"No backoff strategy registered under name '{name}'")
        return cls._registry[name]
