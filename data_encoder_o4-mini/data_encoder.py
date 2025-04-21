import pickle
import zlib
import gzip
import lzma

# Compression algorithm codes
ALG_NONE = 0
ALG_ZLIB = 1
ALG_GZIP = 2
ALG_LZMA = 3

def _check_type(value, expected):
    """Helper to check a single value against expected type descriptor."""
    if expected == "int":
        return type(value) is int
    elif expected == "str":
        return type(value) is str
    elif expected == "bool":
        return type(value) is bool
    elif expected == "dict":
        return type(value) is dict
    else:
        # Unknown expected type
        return False

def _encode_with_schema(data, schema):
    """
    Apply schema to data: fill defaults for missing fields and validate types.
    Schema format:
      { field_name: "int"/"str"/"bool"/"dict" 
        or field_name: [ subtype ] for homogeneous lists }
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dict when using schema")
    result = {}
    # Process schema fields
    for key, expected in schema.items():
        if key in data:
            val = data[key]
            # Validate
            if isinstance(expected, list):
                # Expect a list with homogeneous subtype
                if not isinstance(val, list):
                    raise TypeError(f"Field '{key}' must be a list")
                subtype = expected[0]
                for item in val:
                    if not _check_type(item, subtype):
                        raise TypeError(f"Field '{key}' list item has wrong type")
                # Keep as is
                result[key] = val
            else:
                if not _check_type(val, expected):
                    raise TypeError(f"Field '{key}' has wrong type")
                result[key] = val
        else:
            # Missing field: supply default
            if isinstance(expected, list):
                result[key] = []
            else:
                if expected == "int":
                    result[key] = 0
                elif expected == "str":
                    result[key] = ""
                elif expected == "bool":
                    result[key] = False
                elif expected == "dict":
                    result[key] = {}
                else:
                    # Unknown type in schema
                    raise TypeError(f"Unsupported schema type {expected}")
    # Include any extra keys not in schema
    for key, val in data.items():
        if key not in result:
            result[key] = val
    return result

def _validate_data(obj):
    """
    Recursively validate that obj is composed of supported types:
    int, str, bool, list (homogeneous), set (homogeneous), dict (str keys).
    Raises TypeError on unsupported or mixed types.
    """
    t = type(obj)
    if t is int or t is str or t is bool:
        return
    elif isinstance(obj, list):
        if not obj:
            return
        first_t = type(obj[0])
        # Validate allowed type
        if first_t not in (int, str, bool, list, set, dict):
            raise TypeError("Unsupported element type in list")
        for item in obj:
            if type(item) is not first_t:
                raise TypeError("Mixed types in list")
            _validate_data(item)
    elif isinstance(obj, set):
        if not obj:
            return
        # Get a sample
        it = iter(obj)
        first = next(it)
        first_t = type(first)
        if first_t not in (int, str, bool, list, set, dict):
            raise TypeError("Unsupported element type in set")
        for item in obj:
            if type(item) is not first_t:
                raise TypeError("Mixed types in set")
            _validate_data(item)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if type(k) is not str:
                raise TypeError("Dictionary keys must be strings")
            _validate_data(v)
    else:
        raise TypeError(f"Type {t} not supported")

def encode(data, compress=False, compression_algorithm="zlib", schema=None):
    """
    Encode supported Python data types into bytes.
    If schema is provided, data must be a dict and will be checked/filled by schema.
    Optionally compress the serialized payload.
    """
    # Schema processing
    if schema is not None:
        data = _encode_with_schema(data, schema)
    # Validate data types
    _validate_data(data)
    # Serialize using pickle
    raw = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    # Decide on compression
    algo_code = ALG_NONE
    payload = raw
    if compress:
        # Choose compressor
        alg = compression_algorithm.lower()
        if alg == "zlib":
            comp_func = zlib.compress
            code = ALG_ZLIB
        elif alg == "gzip":
            comp_func = gzip.compress
            code = ALG_GZIP
        elif alg == "lzma":
            comp_func = lzma.compress
            code = ALG_LZMA
        else:
            raise ValueError(f"Unknown compression algorithm '{compression_algorithm}'")
        # Attempt compression
        compressed = comp_func(raw)
        # Use compression only if it shrinks data
        if len(compressed) < len(raw):
            algo_code = code
            payload = compressed
        else:
            algo_code = ALG_NONE
            payload = raw
    # Build final bytes: first byte = algo code, rest = payload
    return bytes([algo_code]) + payload

def decode(blob, field=None):
    """
    Decode bytes produced by encode(). Optionally extract a single field by name.
    """
    if not isinstance(blob, (bytes, bytearray)) or len(blob) < 1:
        raise ValueError("Invalid blob for decoding")
    code = blob[0]
    payload = blob[1:]
    # Decompress if needed
    if code == ALG_NONE:
        raw = payload
    elif code == ALG_ZLIB:
        raw = zlib.decompress(payload)
    elif code == ALG_GZIP:
        raw = gzip.decompress(payload)
    elif code == ALG_LZMA:
        raw = lzma.decompress(payload)
    else:
        raise ValueError(f"Unknown encoding header: {code}")
    # Deserialize
    try:
        data = pickle.loads(raw)
    except Exception as e:
        raise ValueError("Failed to deserialize data") from e
    # Field extraction
    if field is None:
        return data
    # Field-level access
    if not isinstance(data, dict):
        raise ValueError("Field specified but decoded data is not a dict")
    if field not in data:
        raise ValueError(f"Field '{field}' not found")
    return data[field]
