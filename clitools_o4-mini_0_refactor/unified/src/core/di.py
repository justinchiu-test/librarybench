"""
Dependency injection container.
"""
import inspect

_container = None

class Container:
    def __init__(self, deps):
        self._instances = {}
        for key, val in deps.items():
            if isinstance(val, type):
                self._instances[key] = val()
            else:
                self._instances[key] = val

    def resolve(self, name):
        if name not in self._instances:
            raise KeyError(name)
        return self._instances[name]

def init_di(deps):
    global _container
    _container = Container(deps)
    return _container

def inject(func):
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            if name not in kwargs and _container is not None:
                try:
                    kwargs[name] = _container.resolve(name)
                except KeyError:
                    pass
        return func(*args, **kwargs)
    return wrapper