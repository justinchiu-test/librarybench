import zlib
import base64
from typing import Any, Dict
from utils import transform_dict, transform_list, compress_str, decompress_entry

def validate_data(data: Any, schema: Any) -> bool:
    """
    Validate data against the provided schema.
    Schema can be:
      - a Python type (e.g., int, str)
      - a dict mapping keys to subschemas
      - a list with one element that is the subschema for list items
    Raises TypeError or KeyError on mismatch.
    """
    if isinstance(schema, type):
        if not isinstance(data, schema):
            raise TypeError(f'Expected type {schema.__name__}, got {type(data).__name__}')
        return True

    if isinstance(schema, dict):
        if not isinstance(data, dict):
            raise TypeError(f'Expected dict, got {type(data).__name__}')
        for key, subschema in schema.items():
            if key not in data:
                raise KeyError(f'Missing key: {key}')
            validate_data(data[key], subschema)
        return True

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
            encoded[key] = {'type': 'dict', 'value': encode_dictionary(value)}
        elif isinstance(value, list):
            encoded_list = []
            for item in value:
                encoded_list.append({'type': type(item).__name__, 'value': item})
            encoded[key] = {'type': 'list', 'value': encoded_list}
        else:
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
                lst.append(item['value'])
            decoded[key] = lst
        else:
            decoded[key] = val
    return decoded


def compress_long_strings(data: Any, threshold: int = 10) -> Any:
    """
    Recursively compress any string longer than `threshold` using zlib + base64.
    """
    if isinstance(data, str):
        return compress_str(data, threshold)
    if isinstance(data, dict):
        return transform_dict(data, lambda v: compress_long_strings(v, threshold))
    if isinstance(data, list):
        return transform_list(data, lambda v: compress_long_strings(v, threshold))
    return data


def decompress_long_strings(data: Any) -> Any:
    """
    Recursively decompress data encoded by compress_long_strings.
    """
    decompressed = decompress_entry(data)
    if decompressed is not None:
        return decompressed
    if isinstance(data, dict):
        return transform_dict(data, decompress_long_strings)
    if isinstance(data, list):
        return transform_list(data, decompress_long_strings)
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

    validate_data(raw_data, schema)

    compressed = compress_long_strings(raw_data)
    decompressed = decompress_long_strings(compressed)

    encoded = encode_dictionary(raw_data)
    decoded = decode_dictionary(encoded)

    return {
        'raw': raw_data,
        'compressed': compressed,
        'decompressed': decompressed,
        'encoded': encoded,
        'decoded': decoded
    }
