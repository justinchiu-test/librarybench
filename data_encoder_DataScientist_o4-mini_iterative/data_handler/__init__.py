import json
import zlib

def encode_data(data, schema):
    """
    Encode `data` according to `schema`. The schema is a dict mapping field names
    to expected Python types (e.g., int, str, list, dict).
    Returns a JSON string of the validated data.
    Raises:
        TypeError: if data is not a dict or field type mismatches.
        KeyError: if a required key is missing.
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dict")
    validated = {}
    for key, expected_type in schema.items():
        if key not in data:
            raise KeyError(f"Missing key: {key}")
        value = data[key]
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Key '{key}' expected type {expected_type.__name__}, got {type(value).__name__}"
            )
        validated[key] = value
    return json.dumps(validated)

def decode_data(encoded_data, schema):
    """
    Decode `encoded_data` (a JSON string) according to `schema`.
    Returns the dict of validated data.
    Raises:
        ValueError: if JSON is invalid.
        TypeError: if decoded object is not a dict or field type mismatches.
        KeyError: if a required key is missing.
    """
    try:
        data = json.loads(encoded_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid encoded data: {e}")
    if not isinstance(data, dict):
        raise TypeError("Decoded data is not a dict")
    for key, expected_type in schema.items():
        if key not in data:
            raise KeyError(f"Missing key: {key}")
        value = data[key]
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Key '{key}' expected type {expected_type.__name__}, got {type(value).__name__}"
            )
    return data

def compress_data(data):
    """
    Compress `data` using zlib.
    - If data is str, encodes to UTF-8.
    - If data is bytes/bytearray, uses it directly.
    - Otherwise, serializes to JSON then to UTF-8.
    Returns compressed bytes.
    """
    if isinstance(data, str):
        raw = data.encode('utf-8')
    elif isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
    else:
        raw = json.dumps(data).encode('utf-8')
    return zlib.compress(raw)

def integration_test():
    """
    A simple integration test that:
    1. Defines a sample schema and data.
    2. Encodes, compresses, decompresses, decodes.
    3. Asserts equality.
    Returns True on success.
    """
    schema = {'id': int, 'name': str, 'values': list}
    data = {'id': 123, 'name': 'test', 'values': [1, 2, 3]}
    encoded = encode_data(data, schema)
    compressed = compress_data(encoded)
    decompressed = zlib.decompress(compressed).decode('utf-8')
    decoded = decode_data(decompressed, schema)
    assert decoded == data
    return True
