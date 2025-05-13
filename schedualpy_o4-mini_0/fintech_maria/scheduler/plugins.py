_serializer_plugins = []
_transport_plugins = []

def load_plugin(plugin):
    """
    Plugin must have 'serializer' and 'transport' attributes.
    """
    if hasattr(plugin, 'serializer'):
        _serializer_plugins.append(plugin.serializer)
    if hasattr(plugin, 'transport'):
        _transport_plugins.append(plugin.transport)

def get_serializer_plugins():
    return list(_serializer_plugins)

def get_transport_plugins():
    return list(_transport_plugins)
