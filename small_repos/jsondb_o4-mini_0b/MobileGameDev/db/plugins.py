class PluginManager:
    def __init__(self):
        self._plugins = []

    def register(self, plugin):
        self._plugins.append(plugin)

    def run_hook(self, hook_name, *args, **kwargs):
        for plugin in self._plugins:
            hook = getattr(plugin, hook_name, None)
            if callable(hook):
                hook(*args, **kwargs)
