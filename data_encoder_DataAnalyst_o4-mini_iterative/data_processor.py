import zlib
import base64
from typing import Any, Dict


def validate_data(data: Any, schema: Any) -> bool:
    """
    Validate data against the provided schema.
    Schema can be:
      - a Python type (e.g., int, str)
      - a dict mapping keys to subschemas
      - a list with one element that is the subschema for list items
    Raises TypeError or KeyError on mismatch.
    """
    # Simple type
    if isinstance(schema, type):
        if not isinstance(data, schema):
            raise TypeError(f'Expected type {schema.__name__}, got {type(data).__name__}')
        return True

    # Dict schema
    if isinstance(schema, dict):
        if not isinstance(data, dict):
            raise TypeError(f'Expected dict, got {type(data).__name__}')
        for key, subschema in schema.items():
            if key not in data:
                raise KeyError(f'Missing key: {key}')
            validate_data(data[key], subschema)
        return True

    # List schema (single-element list)
    if isinstance(schema, list):
        if len(schema) != 1:
            raise ValueError('List schema must have exactly one element')
        subschema = schema[0]
        if not isinstance(data, list):
            raise TypeError(f'Expected list, got {type(data).__name__}')
        for item in data:
            validate_data(item, subschema)
        return True

    raise ValueError(f'Invalid schema: {schema}')


def encode_dictionary(data: Dict[Any, Any]) -> Dict[str, Any]:
    """
    Encode a (possibly non-homogeneous) dictionary by tagging each value with its type.
    Supports nested dicts and lists.
    """
    if not isinstance(data, dict):
        raise TypeError('encode_dictionary expects a dict')
    encoded: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            # Nested dict: recurse
            encoded[key] = {'type': 'dict', 'value': encode_dictionary(value)}
        elif isinstance(value, list):
            # List: tag each element
            encoded_list = []
            for item in value:
                encoded_list.append({'type': type(item).__name__, 'value': item})
            encoded[key] = {'type': 'list', 'value': encoded_list}
        else:
            # Primitive
            encoded[key] = {'type': type(value).__name__, 'value': value}
    return encoded


def decode_dictionary(encoded: Dict[str, Any]) -> Dict[Any, Any]:
    """
    Decode a dictionary that was encoded with encode_dictionary back to its original form.
    """
    if not isinstance(encoded, dict):
        raise TypeError('decode_dictionary expects a dict')
    decoded: Dict[Any, Any] = {}
    for key, entry in encoded.items():
        if not isinstance(entry, dict) or 'type' not in entry or 'value' not in entry:
            raise ValueError('Invalid encoded entry for key: {}'.format(key))
        typ = entry['type']
        val = entry['value']
        if typ == 'dict':
            decoded[key] = decode_dictionary(val)
        elif typ == 'list':
            lst = []
            for item in val:
                # item is a dict with 'type' and 'value', drop type after decode
                lst.append(item['value'])
            decoded[key] = lst
        else:
            decoded[key] = val
    return decoded


def compress_long_strings(data: Any, threshold: int = 10) -> Any:
    """
    Recursively compress any string longer than `threshold` using zlib + base64.
    Compressed strings are represented as:
      { '__compressed__': True, 'data': <base64-encoded-compressed-bytes> }
    """
    if isinstance(data, str):
        if len(data) > threshold:
            compressed_bytes = zlib.compress(data.encode('utf-8'))
            b64 = base64.b64encode(compressed_bytes).decode('ascii')
            return {'__compressed__': True, 'data': b64}
        else:
            return data

    if isinstance(data, dict):
        return {k: compress_long_strings(v, threshold) for k, v in data.items()}

    if isinstance(data, list):
        return [compress_long_strings(v, threshold) for v in data]

    # Other types are returned as-is
    return data


def decompress_long_strings(data: Any) -> Any:
    """
    Recursively decompress data encoded by compress_long_strings.
    """
    if isinstance(data, dict) and data.get('__compressed__') and 'data' in data:
        compressed_bytes = base64.b64decode(data['data'])
        text = zlib.decompress(compressed_bytes).decode('utf-8')
        return text

    if isinstance(data, dict):
        return {k: decompress_long_strings(v) for k, v in data.items()}

    if isinstance(data, list):
        return [decompress_long_strings(v) for v in data]

    return data


def example_use_cases() -> Dict[str, Any]:
    """
    Demonstrate the library functionality: validation, compression, encoding.
    Returns a dict containing raw, validated, compressed, decompressed, encoded, and decoded data.
    """
    raw_data = {
        'name': 'Alice',
        'age': 30,
        'notes': 'This is a long note that should be compressed.',
        'tags': ['data', 'analysis', 'compression']
    }
    schema = {
        'name': str,
        'age': int,
        'notes': str,
        'tags': [str]
    }

    # Validate
    validate_data(raw_data, schema)

    # Compress / Decompress
    compressed = compress_long_strings(raw_data)
    decompressed = decompress_long_strings(compressed)

    # Encode / Decode dictionary
    encoded = encode_dictionary(raw_data)
    decoded = decode_dictionary(encoded)

    return {
        'raw': raw_data,
        'compressed': compressed,
        'decompressed': decompressed,
        'encoded': encoded,
        'decoded': decoded
    }
