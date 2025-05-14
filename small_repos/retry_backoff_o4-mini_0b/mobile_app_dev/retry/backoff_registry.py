class BackoffRegistry:
    _strategies = {}

    @classmethod
    def register(cls, name, strategy_cls):
        cls._strategies[name] = strategy_cls

    @classmethod
    def get(cls, name):
        return cls._strategies.get(name)

    @classmethod
    def clear(cls):
        cls._strategies.clear()
