import math

class BackoffRegistry:
    _registry = {}

    @classmethod
    def register(cls, name, func):
        cls._registry[name] = func
        return func

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)

def constant_backoff(attempt, base=1):
    return base

def exponential_backoff(attempt, base=1, factor=2):
    return base * (factor ** (attempt - 1))

# Pre-register built-in backoffs
BackoffRegistry.register("constant", constant_backoff)
BackoffRegistry.register("exponential", exponential_backoff)
