import json
import pickle

try:
    import msgpack
except ImportError:
    msgpack = None

def serialize_job(obj, format='json'):
    if format == 'json':
        return json.dumps(obj).encode()
    elif format == 'pickle':
        return pickle.dumps(obj)
    elif format == 'msgpack':
        if not msgpack:
            raise ImportError('msgpack not available')
        return msgpack.packb(obj)
    else:
        raise ValueError('Unknown format')

def deserialize_job(data, format='json'):
    if format == 'json':
        return json.loads(data.decode())
    elif format == 'pickle':
        return pickle.loads(data)
    elif format == 'msgpack':
        if not msgpack:
            raise ImportError('msgpack not available')
        return msgpack.unpackb(data, strict_map_key=False)
    else:
        raise ValueError('Unknown format')
