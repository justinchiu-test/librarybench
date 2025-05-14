_plugins = {}

def register_field_plugin(name, plugin_class):
    if name in _plugins:
        raise ValueError("Plugin already registered")
    _plugins[name] = plugin_class

def get_plugin(name):
    return _plugins.get(name)
