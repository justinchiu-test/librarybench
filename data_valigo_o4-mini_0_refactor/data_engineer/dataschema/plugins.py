class PluginManager:
    def __init__(self):
        self._plugins = {}

    def register(self, name: str, plugin):
        self._plugins[name] = plugin

    def get(self, name: str):
        return self._plugins.get(name)

    def list(self):
        return list(self._plugins.keys())
