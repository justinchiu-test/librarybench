class CICDPluginManager:
    """Manager for CICD plugins to trigger on events."""
    def __init__(self):
        self._plugins = []

    def register(self, plugin):
        """Register a plugin callable that takes an Event."""
        self._plugins.append(plugin)

    def trigger(self, event):
        """Trigger all registered plugins with the event."""
        for plugin in self._plugins:
            plugin(event)
