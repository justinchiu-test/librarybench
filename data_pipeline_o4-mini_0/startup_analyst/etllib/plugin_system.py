class PluginSystem:
    _registry = {}

    @classmethod
    def register(cls, plugin_type, name, plugin_cls):
        cls._registry.setdefault(plugin_type, {})[name] = plugin_cls

    @classmethod
    def get(cls, plugin_type, name):
        return cls._registry.get(plugin_type, {}).get(name)
