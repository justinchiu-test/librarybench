class PluginManager:
    def __init__(self):
        self.plugins = []

    def register(self, plugin):
        self.plugins.append(plugin)

    def apply_hook(self, hook_name, *args, **kwargs):
        for plugin in self.plugins:
            hook = getattr(plugin, hook_name, None)
            if callable(hook):
                hook(*args, **kwargs)
