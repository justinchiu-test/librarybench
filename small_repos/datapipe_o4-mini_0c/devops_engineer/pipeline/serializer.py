_serializers = {}

def register_serializer(name, cls):
    _serializers[name] = cls

def get_serializer(name):
    return _serializers.get(name)
