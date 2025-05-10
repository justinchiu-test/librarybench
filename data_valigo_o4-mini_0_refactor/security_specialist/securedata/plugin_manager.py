class PluginManager:
    def __init__(self):
        self._plugins = {}

    def register(self, name: str, plugin):
        self._plugins.setdefault(name, []).append(plugin)

    def get(self, name: str):
        return self._plugins.get(name, [])

    def list_plugins(self):
        return dict(self._plugins)
