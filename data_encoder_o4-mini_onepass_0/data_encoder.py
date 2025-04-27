import struct
import zlib
import gzip
import lzma

# Type tags
TYPE_INT   = 1
TYPE_STR   = 2
TYPE_BOOL  = 3
TYPE_LIST  = 4
TYPE_SET   = 5
TYPE_DICT  = 6
TYPE_COMP  = 7

# Compression threshold (bytes)
_COMPRESSION_THRESHOLD = 100

# Compression algorithm mapping
_COMPRESSION_ALGS = {
    'zlib': 1,
    'gzip': 2,
    'lzma': 3
}
_REV_COMPRESSION_ALGS = {v: k for k, v in _COMPRESSION_ALGS.items()}


class _ByteReader:
    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0
        self._len = len(data)

    def read(self, n: int) -> bytes:
        if self._pos + n > self._len:
            raise ValueError("Unexpected end of data")
        res = self._data[self._pos:self._pos+n]
        self._pos += n
        return res

    def peek(self) -> int:
        if self._pos >= self._len:
            raise ValueError("No more data")
        return self._data[self._pos]

    def eof(self) -> bool:
        return self._pos >= self._len


def encode(obj, schema=None, compress=False, compression_algorithm='zlib'):
    """
    Encode an object into our custom binary format.
    If schema is provided, use schema-based encoding.
    Optionally compress the final bytes.
    """
    if schema is not None:
        raw = _encode_with_schema(schema, obj)
    else:
        raw = _encode_obj(obj)

    if compress:
        # Skip compression if data too small
        if len(raw) < _COMPRESSION_THRESHOLD:
            return raw
        alg = compression_algorithm.lower()
        if alg not in _COMPRESSION_ALGS:
            raise ValueError(f"Unknown compression algorithm: {compression_algorithm}")
        alg_id = _COMPRESSION_ALGS[alg]
        if alg == 'zlib':
            cdata = zlib.compress(raw)
        elif alg == 'gzip':
            cdata = gzip.compress(raw)
        elif alg == 'lzma':
            cdata = lzma.compress(raw)
        else:
            # should not happen
            raise ValueError(f"Unsupported compression algorithm: {compression_algorithm}")
        # Wrap with compression header
        return bytes([TYPE_COMP, alg_id]) + cdata

    return raw


def _encode_obj(obj):
    """Encode object without schema."""
    # Bool must come before int check
    if isinstance(obj, bool):
        return bytes([TYPE_BOOL, 1 if obj else 0])
    elif isinstance(obj, int) and not isinstance(obj, bool):
        # 8-byte signed big-endian
        return bytes([TYPE_INT]) + struct.pack('>q', obj)
    elif isinstance(obj, str):
        b = obj.encode('utf-8')
        return bytes([TYPE_STR]) + struct.pack('>I', len(b)) + b
    elif isinstance(obj, list):
        # Homogeneous check
        if not obj:
            # empty list
            content = b''
        else:
            first = obj[0]
            for item in obj:
                if type(item) is not type(first):
                    raise TypeError("Non-homogeneous list")
            # encode items
            content = b''.join(_encode_obj(item) for item in obj)
        return bytes([TYPE_LIST]) + struct.pack('>I', len(obj)) + content
    elif isinstance(obj, set):
        # Homogeneous check
        items = list(obj)
        if not items:
            content = b''
        else:
            first = items[0]
            for item in items:
                if type(item) is not type(first):
                    raise TypeError("Non-homogeneous set")
            # sort for deterministic
            try:
                items = sorted(items)
            except Exception:
                pass
            content = b''.join(_encode_obj(item) for item in items)
        return bytes([TYPE_SET]) + struct.pack('>I', len(items)) + content
    elif isinstance(obj, dict):
        # keys must be str
        for k in obj:
            if not isinstance(k, str):
                raise TypeError("Dict keys must be strings")
        items = list(obj.items())
        content = b''.join(
            _encode_obj(k) + _encode_obj(v) for k, v in items
        )
        return bytes([TYPE_DICT]) + struct.pack('>I', len(items)) + content
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")


def _default_for_schema(expected):
    if expected == 'int':
        return 0
    if expected == 'str':
        return ''
    if expected == 'bool':
        return False
    if expected == 'dict':
        return {}
    if isinstance(expected, list) and len(expected) == 1:
        return []
    raise TypeError(f"Cannot determine default for schema type: {expected}")


def _encode_with_schema(schema: dict, data: dict):
    """Encode a dict using a user-defined schema."""
    if not isinstance(data, dict):
        raise TypeError("Data must be a dict when using schema")
    # Prepare fields
    fields = []
    for key, expected in schema.items():
        # Determine actual value or default
        if key in data:
            val = data[key]
        else:
            val = _default_for_schema(expected)
        # Validate type
        if isinstance(expected, str):
            if expected == 'int':
                if not (isinstance(val, int) and not isinstance(val, bool)):
                    raise TypeError(f"Field {key} expected int")
            elif expected == 'str':
                if not isinstance(val, str):
                    raise TypeError(f"Field {key} expected str")
            elif expected == 'bool':
                if not isinstance(val, bool):
                    raise TypeError(f"Field {key} expected bool")
            elif expected == 'dict':
                if not isinstance(val, dict):
                    raise TypeError(f"Field {key} expected dict")
            else:
                raise TypeError(f"Unknown schema type: {expected}")
        elif isinstance(expected, list) and len(expected) == 1 and isinstance(expected[0], str):
            subtype = expected[0]
            if not isinstance(val, list):
                raise TypeError(f"Field {key} expected list")
            # Validate element types
            for item in val:
                if subtype == 'int':
                    if not (isinstance(item, int) and not isinstance(item, bool)):
                        raise TypeError(f"Field {key} expected list of int")
                elif subtype == 'str':
                    if not isinstance(item, str):
                        raise TypeError(f"Field {key} expected list of str")
                elif subtype == 'bool':
                    if not isinstance(item, bool):
                        raise TypeError(f"Field {key} expected list of bool")
                elif subtype == 'dict':
                    if not isinstance(item, dict):
                        raise TypeError(f"Field {key} expected list of dict")
                else:
                    raise TypeError(f"Unknown list schema subtype: {subtype}")
        else:
            raise TypeError(f"Invalid schema for field {key}: {expected}")
        # Encode key and value
        fields.append(_encode_obj(key))
        fields.append(_encode_obj(val))
    # Build dict encoding
    content = b''.join(fields)
    return bytes([TYPE_DICT]) + struct.pack('>I', len(schema)) + content


def decode(data: bytes, field=None):
    """
    Decode bytes into Python object. If field is provided, extract only that field
    from a top-level dict.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("decode input must be bytes")
    buf = bytes(data)  # ensure immutable bytes
    # Handle top-level compression
    if buf and buf[0] == TYPE_COMP:
        # compressed
        if len(buf) < 2:
            raise ValueError("Invalid compressed data")
        alg_id = buf[1]
        alg = _REV_COMPRESSION_ALGS.get(alg_id)
        if alg is None:
            raise ValueError("Unknown compression algorithm in data")
        cdata = buf[2:]
        if alg == 'zlib':
            raw = zlib.decompress(cdata)
        elif alg == 'gzip':
            raw = gzip.decompress(cdata)
        elif alg == 'lzma':
            raw = lzma.decompress(cdata)
        else:
            raise ValueError("Unsupported compression algorithm in data")
        buf = raw

    reader = _ByteReader(buf)
    if field is None:
        val = _decode_all(reader)
        return val
    else:
        # field-level access
        # must be dict
        if reader.peek() != TYPE_DICT:
            raise ValueError("Field-level access on non-dict")
        # consume dict header
        reader.read(1)
        count = struct.unpack('>I', reader.read(4))[0]
        for _ in range(count):
            # read key
            key = _decode_all(reader)
            if not isinstance(key, str):
                raise ValueError("Invalid dict key type")
            if key == field:
                # found; decode value and return
                return _decode_all(reader)
            else:
                # skip value
                _skip_value(reader)
        # not found
        raise ValueError(f"Field {field} not found")


def _decode_all(reader: _ByteReader):
    """Decode value at reader's position."""
    t = reader.read(1)[0]
    if t == TYPE_INT:
        raw = reader.read(8)
        val = struct.unpack('>q', raw)[0]
        return val
    elif t == TYPE_STR:
        raw = reader.read(4)
        length = struct.unpack('>I', raw)[0]
        data = reader.read(length)
        return data.decode('utf-8')
    elif t == TYPE_BOOL:
        b = reader.read(1)[0]
        if b == 1:
            return True
        elif b == 0:
            return False
        else:
            raise ValueError("Invalid boolean value")
    elif t == TYPE_LIST:
        raw = reader.read(4)
        count = struct.unpack('>I', raw)[0]
        lst = []
        for _ in range(count):
            lst.append(_decode_all(reader))
        return lst
    elif t == TYPE_SET:
        raw = reader.read(4)
        count = struct.unpack('>I', raw)[0]
        s = set()
        for _ in range(count):
            s.add(_decode_all(reader))
        return s
    elif t == TYPE_DICT:
        raw = reader.read(4)
        count = struct.unpack('>I', raw)[0]
        d = {}
        for _ in range(count):
            key = _decode_all(reader)
            if not isinstance(key, str):
                raise ValueError("Invalid dict key type")
            val = _decode_all(reader)
            d[key] = val
        return d
    else:
        raise ValueError(f"Invalid type header: {t}")


def _skip_value(reader: _ByteReader):
    """Skip over one encoded value."""
    t = reader.read(1)[0]
    if t == TYPE_INT:
        reader.read(8)
    elif t == TYPE_STR:
        raw = reader.read(4)
        length = struct.unpack('>I', raw)[0]
        reader.read(length)
    elif t == TYPE_BOOL:
        reader.read(1)
    elif t in (TYPE_LIST, TYPE_SET):
        raw = reader.read(4)
        count = struct.unpack('>I', raw)[0]
        for _ in range(count):
            _skip_value(reader)
    elif t == TYPE_DICT:
        raw = reader.read(4)
        count = struct.unpack('>I', raw)[0]
        for _ in range(count):
            _skip_value(reader)  # key
            _skip_value(reader)  # value
    else:
        # Unexpected or unsupported nested compression
        raise ValueError(f"Cannot skip unknown type: {t}")
