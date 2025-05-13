class PluginArchitecture:
    def __init__(self):
        self._plugins = {}

    def register_plugin(self, plugin_type, plugin):
        if plugin_type not in self._plugins:
            self._plugins[plugin_type] = []
        self._plugins[plugin_type].append(plugin)

    def get_plugins(self, plugin_type):
        return list(self._plugins.get(plugin_type, []))
