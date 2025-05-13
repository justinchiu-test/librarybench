"""
Dependency injection for data_scientist datapipeline CLI.
"""
class Container:
    def __init__(self, deps):
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
    return Container(deps)