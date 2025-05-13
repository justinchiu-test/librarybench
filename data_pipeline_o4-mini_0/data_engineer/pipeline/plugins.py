import importlib

class PluginSystem:
    def __init__(self):
        self.registry = {}

    def register(self, name, obj):
        self.registry[name] = obj

    def get(self, name):
        return self.registry.get(name)

    def load_module(self, module_name):
        mod = importlib.import_module(module_name)
        return mod
