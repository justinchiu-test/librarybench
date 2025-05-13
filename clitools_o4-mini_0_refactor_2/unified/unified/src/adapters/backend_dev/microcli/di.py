"""
Dependency injection container for backend_dev microcli.
"""
class Container:
    def __init__(self, deps):
        # deps: dict name -> factory/class
        self._deps = deps
        self._instances = {}
    def resolve(self, name):
        if name in self._instances:
            return self._instances[name]
        if name not in self._deps:
            raise KeyError(name)
        inst = self._deps[name]()
        self._instances[name] = inst
        return inst

def init_di(deps):
    """Initialize the DI container with a dict of dependencies."""
    return Container(deps)