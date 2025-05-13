class PluginManager:
    def __init__(self):
        self._transports = {}
        self._serializers = {}

    def register_transport(self, name, cls):
        self._transports[name] = cls

    def get_transport(self, name):
        return self._transports.get(name)

    def register_serializer(self, name, cls):
        self._serializers[name] = cls

    def get_serializer(self, name):
        return self._serializers.get(name)
