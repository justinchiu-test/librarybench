class PluginSystem:
    def __init__(self):
        self.adapters = {}

    def register(self, name, fn):
        self.adapters[name] = fn

    def adapt(self, name, *args, **kwargs):
        if name not in self.adapters:
            raise KeyError(f"No adapter registered for {name}")
        return self.adapters[name](*args, **kwargs)
