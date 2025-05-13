import threading

class PluginManager:
    def __init__(self):
        self._serializers = {}
        self._transports = {}
        self._lock = threading.Lock()

    def register_serializer(self, name, serializer):
        with self._lock:
            self._serializers[name] = serializer

    def register_transport(self, name, transport):
        with self._lock:
            self._transports[name] = transport

    def get_serializer(self, name):
        return self._serializers.get(name)

    def get_transport(self, name):
        return self._transports.get(name)
