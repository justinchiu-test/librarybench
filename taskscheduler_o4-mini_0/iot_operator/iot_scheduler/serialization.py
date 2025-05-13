import pickle
try:
    import msgpack
    _has_msgpack = True
except ImportError:
    _has_msgpack = False

def serialize_job(obj, method='pickle'):
    if method == 'msgpack' and _has_msgpack:
        return msgpack.packb(obj)
    return pickle.dumps(obj)

def deserialize_job(data, method='pickle'):
    if method == 'msgpack' and _has_msgpack:
        return msgpack.unpackb(data)
    return pickle.loads(data)
