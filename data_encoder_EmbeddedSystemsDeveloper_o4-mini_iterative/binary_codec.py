import struct


class BinaryCodecError(Exception):
    """Custom exception for binary codec errors."""
    pass


def encode_binary(data, schema):
    """
    Encode a data dictionary into bytes according to the provided schema.
    
    :param data: dict of values to encode.
    :param schema: list of tuples (key, format_or_nested_schema). If the second
                   element is a string, it's a struct format; if it's a list,
                   it's a nested schema.
    :return: bytes object of packed data.
    :raises BinaryCodecError: on missing keys or packing errors.
    """
    def _pack(d, sch):
        buf = bytearray()
        for key, fmt in sch:
            if isinstance(fmt, list):
                # nested structure
                if key not in d or not isinstance(d[key], dict):
                    raise BinaryCodecError(f"Expected dict for nested field '{key}'")
                buf.extend(_pack(d[key], fmt))
            else:
                # flat field
                if key not in d:
                    raise BinaryCodecError(f"Missing key '{key}' in data")
                try:
                    buf.extend(struct.pack(fmt, d[key]))
                except Exception as e:
                    raise BinaryCodecError(f"Error packing field '{key}': {e}")
        return bytes(buf)

    return _pack(data, schema)


def decode_binary(encoded_data, schema):
    """
    Decode bytes into a data dictionary according to the provided schema.
    
    :param encoded_data: bytes object to decode.
    :param schema: list of tuples (key, format_or_nested_schema).
    :return: dict of decoded values.
    :raises BinaryCodecError: on unpacking errors or insufficient data.
    """
    def _unpack(data_bytes, sch, offset=0):
        result = {}
        for key, fmt in sch:
            if isinstance(fmt, list):
                # nested
                nested_val, offset = _unpack(data_bytes, fmt, offset)
                result[key] = nested_val
            else:
                size = struct.calcsize(fmt)
                if offset + size > len(data_bytes):
                    raise BinaryCodecError(f"Not enough bytes to unpack field '{key}'")
                try:
                    val = struct.unpack(fmt, data_bytes[offset:offset + size])[0]
                except Exception as e:
                    raise BinaryCodecError(f"Error unpacking field '{key}': {e}")
                result[key] = val
                offset += size
        return result, offset

    decoded, used = _unpack(encoded_data, schema, 0)
    # it's acceptable if extra bytes remain, but warn?
    return decoded


def handle_nested_structures(data, parent_key='', sep='.'):
    """
    Flatten a nested dictionary into a single-level dict with dot-separated keys.
    
    :param data: nested dict.
    :param parent_key: (used internally) prefix for keys.
    :param sep: separator string.
    :return: flattened dict.
    """
    items = {}
    for k, v in data.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.update(handle_nested_structures(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def error_handling_process(func, *args, **kwargs):
    """
    Wrapper that executes func with args and kwargs, catching BinaryCodecError
    and other exceptions.
    
    :return: tuple (success: bool, result or error message).
    """
    try:
        res = func(*args, **kwargs)
        return True, res
    except Exception as e:
        return False, str(e)
