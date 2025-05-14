_serializers = {}

def register_serializer(name, serializer_class):
    _serializers[name] = serializer_class

def get_serializer(name):
    return _serializers.get(name)
