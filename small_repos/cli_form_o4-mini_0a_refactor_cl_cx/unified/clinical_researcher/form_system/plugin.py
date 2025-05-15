_PLUGINS = {}

def register_field_plugin(name, cls):
    """
    Register a plugin class under a given name.
    """
    if name in _PLUGINS:
        raise KeyError(f"Plugin '{name}' already registered")
    _PLUGINS[name] = cls

def get_field_plugin(name):
    return _PLUGINS.get(name)
