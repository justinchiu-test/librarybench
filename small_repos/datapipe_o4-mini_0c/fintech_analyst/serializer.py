serializers = {}

def register_serializer(name, func):
    if not callable(func):
        raise ValueError("Serializer must be callable")
    serializers[name] = func

def get_serializer(name):
    return serializers.get(name)
