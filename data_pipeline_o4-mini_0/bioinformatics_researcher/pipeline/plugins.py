class PluginManager:
    def __init__(self):
        self.plugins = {}
    def register(self, name, func):
        self.plugins[name] = func
    def execute(self, name, *args, **kwargs):
        if name not in self.plugins:
            raise KeyError(f"No plugin named {name}")
        return self.plugins[name](*args, **kwargs)
    def list_plugins(self):
        return list(self.plugins.keys())
