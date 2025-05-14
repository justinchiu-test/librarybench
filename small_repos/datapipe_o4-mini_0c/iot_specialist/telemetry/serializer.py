_serializers = {}

def register_serializer(name, func):
    _serializers[name] = func

def serialize(name, data):
    if name not in _serializers:
        raise KeyError(f"Serializer {name} not registered")
    return _serializers[name](data)
