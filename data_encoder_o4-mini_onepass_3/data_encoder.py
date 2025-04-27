import struct
import zlib
import gzip
import lzma

# Type tags
TAG_INT = 1
TAG_STR = 2
TAG_BOOL = 3
TAG_LIST = 4
TAG_SET = 5
TAG_DICT = 6
TAG_SCHEMA = 7
TAG_COMPRESSED = 16

# Compression threshold: skip compressing small data
SMALL_COMPRESS_THRESHOLD = 100

# Compression algorithm codes
ALGO_CODES = {
    'zlib': 1,
    'gzip': 2,
    'lzma': 3
}
CODES_ALGO = {v: k for k, v in ALGO_CODES.items()}


def encode(obj, schema=None, compress=False, compression_algorithm='zlib'):
    """
    Encode an object to bytes, optionally with a schema or compression.
    """
    # Schema-aware encoding
    if schema is not None:
        raw = _encode_with_schema(obj, schema)
    else:
        raw = _encode(obj)

    # Optionally compress
    if compress:
        # Only compress if data is large enough
        if len(raw) > SMALL_COMPRESS_THRESHOLD:
            algo = compression_algorithm
            if algo not in ALGO_CODES:
                raise ValueError(f"Unknown compression algorithm: {algo}")
            code = ALGO_CODES[algo]
            if algo == 'zlib':
                comp_data = zlib.compress(raw)
            elif algo == 'gzip':
                comp_data = gzip.compress(raw)
            elif algo == 'lzma':
                comp_data = lzma.compress(raw)
            header = struct.pack('>B', TAG_COMPRESSED)
            header += struct.pack('>B', code)
            header += struct.pack('>I', len(raw))
            return header + comp_data
        # else: skip compress
    return raw


def decode(data, field=None):
    """
    Decode bytes back to an object, or extract a field if schema-encoded.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Data to decode must be bytes")
    buf = bytes(data)
    # Handle compression wrapper
    if len(buf) >= 1 and buf[0] == TAG_COMPRESSED:
        # Decompress
        _, buf = _decompress(buf, 0)
    # Schema?
    if len(buf) >= 1 and buf[0] == TAG_SCHEMA:
        return _decode_with_schema(buf, field)
    # Normal decode
    obj, _ = _decode(buf, 0)
    return obj


def _encode(obj):
    """
    Recursively encode an object without schema or compression.
    """
    # Boolean must come before int check
    if isinstance(obj, bool):
        # TAG_BOOL + 1 byte
        return struct.pack('>B', TAG_BOOL) + (b'\x01' if obj else b'\x00')
    if isinstance(obj, int):
        # TAG_INT + 1-byte length + signed big endian
        # minimal length
        if obj == 0:
            b = b'\x00'
        else:
            length = (obj.bit_length() + 7) // 8
            b = obj.to_bytes(length, byteorder='big', signed=True)
        n = len(b)
        if n > 255:
            raise OverflowError("Integer too large to encode")
        return struct.pack('>B', TAG_INT) + struct.pack('>B', n) + b
    if isinstance(obj, str):
        b = obj.encode('utf-8')
        return struct.pack('>B', TAG_STR) + struct.pack('>I', len(b)) + b
    if isinstance(obj, list):
        # Check homogeneous
        if len(obj) >= 2:
            first_t = type(obj[0])
            for item in obj:
                if type(item) is not first_t:
                    raise TypeError("Lists must be homogeneous")
        # Encode elements
        parts = []
        for item in obj:
            parts.append(_encode(item))
        body = b''.join(parts)
        return struct.pack('>B', TAG_LIST) + struct.pack('>I', len(obj)) + body
    if isinstance(obj, set):
        # Check homogeneous
        if len(obj) >= 2:
            it = iter(obj)
            first = next(it)
            first_t = type(first)
            for item in it:
                if type(item) is not first_t:
                    raise TypeError("Sets must be homogeneous")
        parts = []
        for item in obj:
            parts.append(_encode(item))
        body = b''.join(parts)
        return struct.pack('>B', TAG_SET) + struct.pack('>I', len(obj)) + body
    if isinstance(obj, dict):
        parts = []
        # Keys must be strings
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError("Dictionary keys must be strings")
            parts.append(_encode(k))
            parts.append(_encode(v))
        body = b''.join(parts)
        return struct.pack('>B', TAG_DICT) + struct.pack('>I', len(obj)) + body
    raise TypeError(f"Type {type(obj)} not supported")


def _decode(buf, offset):
    """
    Recursively decode from buf starting at offset.
    Returns (obj, new_offset).
    """
    if offset >= len(buf):
        raise ValueError("Unexpected end of data")
    tag = buf[offset]
    offset += 1

    if tag == TAG_BOOL:
        if offset >= len(buf):
            raise ValueError("Unexpected end of data")
        val = buf[offset]
        offset += 1
        if val == 0:
            return False, offset
        elif val == 1:
            return True, offset
        else:
            raise ValueError("Invalid boolean value")

    if tag == TAG_INT:
        if offset >= len(buf):
            raise ValueError("Unexpected end of data")
        n = buf[offset]
        offset += 1
        if offset + n > len(buf):
            raise ValueError("Unexpected end of data")
        b = buf[offset:offset + n]
        offset += n
        val = int.from_bytes(b, byteorder='big', signed=True)
        return val, offset

    if tag == TAG_STR:
        if offset + 4 > len(buf):
            raise ValueError("Unexpected end of data")
        length = struct.unpack('>I', buf[offset:offset + 4])[0]
        offset += 4
        if offset + length > len(buf):
            raise ValueError("Unexpected end of data")
        b = buf[offset:offset + length]
        offset += length
        return b.decode('utf-8'), offset

    if tag == TAG_LIST:
        if offset + 4 > len(buf):
            raise ValueError("Unexpected end of data")
        count = struct.unpack('>I', buf[offset:offset + 4])[0]
        offset += 4
        lst = []
        for _ in range(count):
            item, offset = _decode(buf, offset)
            lst.append(item)
        return lst, offset

    if tag == TAG_SET:
        if offset + 4 > len(buf):
            raise ValueError("Unexpected end of data")
        count = struct.unpack('>I', buf[offset:offset + 4])[0]
        offset += 4
        s = set()
        for _ in range(count):
            item, offset = _decode(buf, offset)
            s.add(item)
        return s, offset

    if tag == TAG_DICT:
        if offset + 4 > len(buf):
            raise ValueError("Unexpected end of data")
        count = struct.unpack('>I', buf[offset:offset + 4])[0]
        offset += 4
        d = {}
        for _ in range(count):
            key, offset = _decode(buf, offset)
            val, offset = _decode(buf, offset)
            d[key] = val
        return d, offset

    raise ValueError(f"Invalid type tag {tag}")


def _decompress(buf, offset):
    """
    Decompress a compressed block at buf[offset]. Returns (new_offset, decompressed_bytes).
    """
    # first byte TAG_COMPRESSED already consumed if offset==0, else consumed above
    # But here we expect buf[offset] == TAG_COMPRESSED
    if buf[offset] != TAG_COMPRESSED:
        raise ValueError("Not a compressed block")
    offset += 1
    if offset >= len(buf):
        raise ValueError("Bad compressed header")
    code = buf[offset]
    offset += 1
    if offset + 4 > len(buf):
        raise ValueError("Bad compressed header")
    orig_len = struct.unpack('>I', buf[offset:offset + 4])[0]
    offset += 4
    comp_data = buf[offset:]
    algo = CODES_ALGO.get(code)
    if algo is None:
        raise ValueError(f"Unknown compression code {code}")
    if algo == 'zlib':
        data = zlib.decompress(comp_data)
    elif algo == 'gzip':
        data = gzip.decompress(comp_data)
    elif algo == 'lzma':
        data = lzma.decompress(comp_data)
    else:
        raise ValueError(f"Unsupported compression algorithm {algo}")
    if len(data) != orig_len:
        # maybe compression changed size? we won't enforce strictly
        pass
    return offset + len(comp_data), data


def _encode_with_schema(obj, schema):
    """
    Encode a dict obj according to user-defined schema.
    """
    if not isinstance(schema, dict):
        raise TypeError("Schema must be a dict")
    if not isinstance(obj, dict):
        raise TypeError("Data must be a dict when schema is provided")

    type_map = {
        'int': int,
        'str': str,
        'bool': bool,
        'dict': dict
    }

    # Prepare field data
    field_names = list(schema.keys())
    field_blobs = []
    # Validate and encode each field
    for field in field_names:
        spec = schema[field]
        if field in obj:
            val = obj[field]
        else:
            # default values
            if isinstance(spec, list):
                val = []
            elif spec == 'int':
                val = 0
            elif spec == 'str':
                val = ""
            elif spec == 'bool':
                val = False
            elif spec == 'dict':
                val = {}
            else:
                raise TypeError(f"Unknown type in schema for field {field}: {spec}")

        # Validate type
        if isinstance(spec, list):
            # List spec
            if len(spec) != 1 or spec[0] not in type_map:
                raise TypeError(f"Invalid list spec for field {field}")
            elem_type = spec[0]
            if not isinstance(val, list):
                raise TypeError(f"Field {field} must be a list")
            for item in val:
                if type(item) is not type_map[elem_type]:
                    raise TypeError(f"Wrong element type in list field {field}")
        else:
            # Simple type
            if spec not in type_map:
                raise TypeError(f"Unknown type in schema for field {field}: {spec}")
            expected = type_map[spec]
            if type(val) is not expected:
                raise TypeError(f"Field {field} must be of type {spec}")

        # Now encode
        blob = _encode(val)
        field_blobs.append(blob)

    # Build header
    header = bytearray()
    header.append(TAG_SCHEMA)
    header += struct.pack('>I', len(field_names))
    # Calculate header size to compute offsets
    # Each entry: 1 byte name len, name bytes, 4 bytes offset, 4 bytes length
    hdr_size = 1 + 4
    for name in field_names:
        name_b = name.encode('utf-8')
        hdr_size += 1 + len(name_b) + 4 + 4

    # Build entries
    data_offset = 0
    for name, blob in zip(field_names, field_blobs):
        name_b = name.encode('utf-8')
        header.append(len(name_b))
        header += name_b
        header += struct.pack('>I', data_offset)
        header += struct.pack('>I', len(blob))
        data_offset += len(blob)

    # Combine header and data
    body = b''.join(field_blobs)
    return bytes(header) + body


def _decode_with_schema(buf, field=None):
    """
    Decode a schema-encoded block, optionally extracting one field.
    """
    offset = 1  # skip TAG_SCHEMA
    if offset + 4 > len(buf):
        raise ValueError("Invalid schema header")
    num_fields = struct.unpack('>I', buf[offset:offset + 4])[0]
    offset += 4
    fields = {}
    for _ in range(num_fields):
        if offset >= len(buf):
            raise ValueError("Invalid schema header")
        name_len = buf[offset]
        offset += 1
        if offset + name_len > len(buf):
            raise ValueError("Invalid schema header")
        name = buf[offset:offset + name_len].decode('utf-8')
        offset += name_len
        if offset + 8 > len(buf):
            raise ValueError("Invalid schema header")
        off = struct.unpack('>I', buf[offset:offset + 4])[0]
        ln = struct.unpack('>I', buf[offset + 4:offset + 8])[0]
        offset += 8
        fields[name] = (off, ln)
    # Data section starts at offset
    data_start = offset
    # Extract one field
    if field is not None:
        if field not in fields:
            raise ValueError(f"Field {field} not in schema")
        off, ln = fields[field]
        blob = buf[data_start + off : data_start + off + ln]
        val, _ = _decode(blob, 0)
        return val
    # Decode all fields
    result = {}
    for name, (off, ln) in fields.items():
        blob = buf[data_start + off : data_start + off + ln]
        val, _ = _decode(blob, 0)
        result[name] = val
    return result
