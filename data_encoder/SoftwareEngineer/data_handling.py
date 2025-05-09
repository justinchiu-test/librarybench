import sys
import struct
import json
from copy import deepcopy

def handle_endianness(data, fmt):
    """
    Convert integer or bytes data to the specified endianness.
    fmt: 'big' or 'little'
    """
    if fmt not in ('big', 'little'):
        raise ValueError("Format must be 'big' or 'little'")
    # If integer, convert to bytes
    if isinstance(data, int):
        # Determine minimum length in bytes
        bitlen = data.bit_length() if data >= 0 else (-data).bit_length() + 1
        length = (bitlen + 7) // 8
        if length == 0:
            length = 1
        return data.to_bytes(length, byteorder=fmt, signed=(data < 0))
    # If bytes or bytearray, reorder if needed
    if isinstance(data, (bytes, bytearray)):
        # If system order matches desired, return as-is
        if sys.byteorder == fmt:
            return bytes(data)
        else:
            # reverse byte sequence
            return bytes(data)[::-1]
    raise TypeError("Data must be int, bytes, or bytearray")


def encode_nested(data, schema):
    """
    Encode a nested data structure according to the provided schema.
    schema: dict mapping field names to types or nested schema dicts.
    Supported types: 'uint8','uint16','uint32','uint64',
                     'int8','int16','int32','int64','string'
    Returns bytes.
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dict")
    if not isinstance(schema, dict):
        raise TypeError("Schema must be a dict")
    encoded_parts = []
    # Check for unexpected keys
    extra_keys = set(data.keys()) - set(schema.keys())
    if extra_keys:
        raise ValueError(f"Unexpected fields in data: {extra_keys}")
    for key, typ in schema.items():
        if key not in data:
            raise KeyError(f"Missing field: {key}")
        value = data[key]
        # Nested schema
        if isinstance(typ, dict):
            encoded_parts.append(encode_nested(value, typ))
        else:
            # Handle primitive types
            if typ == 'string':
                if not isinstance(value, str):
                    raise TypeError(f"Field {key} must be a string")
                raw = value.encode('utf-8')
                # prefix length as uint32 big-endian
                encoded_parts.append(struct.pack('!I', len(raw)))
                encoded_parts.append(raw)
            else:
                # integer types
                fmt_map = {
                    'uint8': '!B', 'uint16': '!H', 'uint32': '!I', 'uint64': '!Q',
                    'int8': '!b', 'int16': '!h', 'int32': '!i', 'int64': '!q'
                }
                if typ not in fmt_map:
                    raise ValueError(f"Unsupported type: {typ}")
                fmt_str = fmt_map[typ]
                try:
                    packed = struct.pack(fmt_str, value)
                except struct.error as e:
                    raise ValueError(f"Error packing field {key}: {e}")
                encoded_parts.append(packed)
    return b''.join(encoded_parts)


def version_schema(schema, version):
    """
    Wrap or tag the schema with a version.
    Returns a new dict with 'version' and 'schema' keys.
    """
    return {'version': version, 'schema': deepcopy(schema)}


def add_metadata(data, metadata):
    """
    Prefix the binary data with a metadata JSON header.
    Header format: 4-byte big-endian length, then JSON-encoded metadata UTF-8 bytes, then data.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Data must be bytes or bytearray")
    if not isinstance(metadata, dict):
        raise TypeError("Metadata must be a dict")
    meta_json = json.dumps(metadata, separators=(',', ':')).encode('utf-8')
    header = struct.pack('!I', len(meta_json)) + meta_json
    return header + data
