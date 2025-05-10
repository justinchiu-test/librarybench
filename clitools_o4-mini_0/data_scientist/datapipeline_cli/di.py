import inspect

_container = {}

def init_di(services):
    _container.update(services)

def inject(func):
    sig = inspect.signature(func)
    def wrapper(*args, **kwargs):
        for name, param in sig.parameters.items():
            if name not in kwargs and name in _container:
                kwargs[name] = _container[name]
        return func(*args, **kwargs)
    return wrapper
