class BackoffRegistry:
    _registry = {}

    @classmethod
    def register(cls, name):
        def decorator(strategy_cls):
            cls._registry[name] = strategy_cls
            return strategy_cls
        return decorator

    @classmethod
    def get(cls, name):
        if name not in cls._registry:
            raise KeyError(f"Backoff strategy '{name}' not found")
        return cls._registry[name]
