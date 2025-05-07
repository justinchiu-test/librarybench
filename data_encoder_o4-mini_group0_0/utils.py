import zlib

def to_bytes(data, *, name='data', allow_str=True):
    """
    Normalize str/bytes/bytearray to bytes.
    If allow_str is False, str is not accepted.
    """
    if isinstance(data, str):
        if not allow_str:
            raise TypeError(f"{name} must be bytes-like, got str")
        return data.encode('utf-8')
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    raise TypeError(f"{name} must be str or bytes-like, got {type(data)}")

def to_str_fallback(b):
    """
    Decode bytes to str, trying utf-8 then latin-1.
    """
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('latin-1')

def require_keys(d, keys):
    """
    Ensure that dict d contains all keys in the keys list.
    """
    for k in keys:
        if k not in d:
            raise KeyError(f"Missing required key: {k}")

def compress_if_smaller(raw):
    """
    zlib-compress the raw bytes and return compressed only if shorter.
    """
    comp = zlib.compress(raw)
    return comp if len(comp) < len(raw) else raw

def validate_type(obj, types, name):
    """
    Check that obj is instance of types, else TypeError.
    """
    if not isinstance(obj, types):
        if isinstance(types, tuple):
            names = ', '.join(t.__name__ for t in types)
        else:
            names = types.__name__
        raise TypeError(f"{name} must be {names}, got {type(obj)}")

def ensure_bytes(data, *, name='data'):
    """
    Ensure data is bytes or bytearray, else ValueError.
    """
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    raise ValueError(f"{name} must be bytes or bytearray")
