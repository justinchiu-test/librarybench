import random

class BackoffRegistry:
    _strategies = {}

    @classmethod
    def register(cls, name, func):
        cls._strategies[name] = func

    @classmethod
    def get(cls, name):
        return cls._strategies[name]

def exponential(base=1, factor=2):
    def strategy(attempt):
        return base * (factor ** (attempt - 1))
    return strategy

def jitter(base=1, factor=2):
    def strategy(attempt):
        return random.uniform(0, base * (factor ** (attempt - 1)))
    return strategy

BackoffRegistry.register('exponential', exponential())
BackoffRegistry.register('jitter', jitter())
