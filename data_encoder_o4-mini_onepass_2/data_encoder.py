import struct
import zlib
import gzip
import lzma

# Type codes
TYPE_INT        = 1
TYPE_STR        = 2
TYPE_BOOL       = 3
TYPE_LIST       = 4
TYPE_SET        = 5
TYPE_DICT       = 6
TYPE_SCHEMA     = 16
TYPE_COMPRESSED = 32

# Compression threshold (bytes)
_COMPRESSION_THRESHOLD = 128

def encode(obj, schema=None, compress=False, compression_algorithm='zlib'):
    """
    Encode an object to our binary format. Optionally with a user-defined schema,
    and optional compression.
    """
    if schema is not None:
        payload = _encode_with_schema(obj, schema)
    else:
        payload = _encode(obj)
    # Handle compression wrapper
    if compress and len(payload) > _COMPRESSION_THRESHOLD:
        # Choose algorithm
        alg = compression_algorithm.lower()
        if alg == 'zlib':
            comp_bytes = zlib.compress(payload)
            alg_code = 1
        elif alg == 'gzip':
            comp_bytes = gzip.compress(payload)
            alg_code = 2
        elif alg == 'lzma':
            comp_bytes = lzma.compress(payload)
            alg_code = 3
        else:
            raise ValueError(f"Unknown compression algorithm: {compression_algorithm}")
        # Build wrapper: code, alg code, original length, then compressed data
        header = bytes([TYPE_COMPRESSED, alg_code]) + struct.pack('>I', len(payload))
        return header + comp_bytes
    else:
        return payload

def decode(data, field=None):
    """
    Decode bytes produced by encode back to Python object.
    If field is provided, only extract that field (schema encoding).
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("decode expects bytes input")
    buf = bytes(data)  # immutable
    if len(buf) < 1:
        raise ValueError("No data to decode")
    # Handle compression wrapper
    if buf[0] == TYPE_COMPRESSED:
        if len(buf) < 6:
            raise ValueError("Invalid compressed data")
        alg_code = buf[1]
        orig_len = struct.unpack('>I', buf[2:6])[0]
        comp_data = buf[6:]
        if alg_code == 1:
            payload = zlib.decompress(comp_data)
        elif alg_code == 2:
            payload = gzip.decompress(comp_data)
        elif alg_code == 3:
            payload = lzma.decompress(comp_data)
        else:
            raise ValueError("Unknown compression code")
        # Optionally verify length
        # if len(payload) != orig_len:
        #     raise ValueError("Decompressed length mismatch")
        buf = payload
    # Handle schema wrapper
    if buf[0] == TYPE_SCHEMA:
        if field is None:
            # decode all fields into a dict
            pos = 1
            if pos >= len(buf):
                raise ValueError("Invalid schema packet")
            num_fields = buf[pos]
            pos += 1
            out = {}
            for _ in range(num_fields):
                if pos >= len(buf):
                    raise ValueError("Invalid schema packet")
                name_len = buf[pos]
                pos += 1
                name = buf[pos:pos+name_len].decode('utf-8')
                pos += name_len
                if pos+4 > len(buf):
                    raise ValueError("Invalid schema packet")
                payload_len = struct.unpack('>I', buf[pos:pos+4])[0]
                pos += 4
                if pos+payload_len > len(buf):
                    raise ValueError("Invalid schema packet")
                field_bytes = buf[pos:pos+payload_len]
                pos += payload_len
                val, _ = _decode(field_bytes, 0)
                out[name] = val
            return out
        else:
            # extract only one field
            pos = 1
            num_fields = buf[pos]
            pos += 1
            for _ in range(num_fields):
                name_len = buf[pos]
                pos += 1
                name = buf[pos:pos+name_len].decode('utf-8')
                pos += name_len
                payload_len = struct.unpack('>I', buf[pos:pos+4])[0]
                pos += 4
                field_bytes = buf[pos:pos+payload_len]
                pos += payload_len
                if name == field:
                    val, _ = _decode(field_bytes, 0)
                    return val
            raise ValueError(f"Field '{field}' not found in schema data")
    else:
        # field-level access only valid for schema
        if field is not None:
            raise ValueError("Field-level access on non-schema data")
        val, end = _decode(buf, 0)
        if end != len(buf):
            # trailing data? ignore or error
            pass
        return val

def _encode(obj):
    """
    Internal encode without schema or compression.
    """
    # Integers (but not bools)
    if isinstance(obj, bool):
        # bool is subclass of int, so test bool first
        return bytes([TYPE_BOOL, 1 if obj else 0])
    if isinstance(obj, int):
        b = struct.pack('>q', obj)
        return bytes([TYPE_INT]) + b
    # Strings
    if isinstance(obj, str):
        b = obj.encode('utf-8')
        return bytes([TYPE_STR]) + struct.pack('>I', len(b)) + b
    # Lists
    if isinstance(obj, list):
        # homogeneous?
        if len(obj) > 0:
            t0 = type(obj[0])
            for e in obj:
                if type(e) is not t0:
                    raise TypeError("Non-homogeneous list")
        # encode elements
        parts = []
        for e in obj:
            parts.append(_encode(e))
        body = b''.join(parts)
        return bytes([TYPE_LIST]) + struct.pack('>I', len(obj)) + body
    # Sets
    if isinstance(obj, set):
        if len(obj) > 0:
            it = iter(obj)
            first = next(it)
            t0 = type(first)
            for e in it:
                if type(e) is not t0:
                    raise TypeError("Non-homogeneous set")
        parts = []
        for e in obj:
            parts.append(_encode(e))
        body = b''.join(parts)
        return bytes([TYPE_SET]) + struct.pack('>I', len(obj)) + body
    # Dictionaries (keys must be strings)
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError("Dictionary keys must be strings")
            ke = _encode(k)
            ve = _encode(v)
            parts.append(ke + ve)
        body = b''.join(parts)
        return bytes([TYPE_DICT]) + struct.pack('>I', len(obj)) + body
    raise TypeError(f"Type {type(obj)} not supported")

def _decode(buf, pos):
    """
    Internal recursive decode.
    Returns (value, new_pos).
    """
    if pos >= len(buf):
        raise ValueError("Unexpected end of data")
    t = buf[pos]
    pos += 1
    # int
    if t == TYPE_INT:
        if pos+8 > len(buf):
            raise ValueError("Unexpected end of int data")
        val = struct.unpack('>q', buf[pos:pos+8])[0]
        pos += 8
        return val, pos
    # str
    if t == TYPE_STR:
        if pos+4 > len(buf):
            raise ValueError("Unexpected end of string length")
        l = struct.unpack('>I', buf[pos:pos+4])[0]
        pos += 4
        if pos+l > len(buf):
            raise ValueError("Unexpected end of string data")
        s = buf[pos:pos+l].decode('utf-8')
        pos += l
        return s, pos
    # bool
    if t == TYPE_BOOL:
        if pos >= len(buf):
            raise ValueError("Unexpected end of bool data")
        v = buf[pos]
        pos += 1
        return bool(v), pos
    # list
    if t == TYPE_LIST:
        if pos+4 > len(buf):
            raise ValueError("Unexpected end of list length")
        n = struct.unpack('>I', buf[pos:pos+4])[0]
        pos += 4
        lst = []
        for _ in range(n):
            v, pos = _decode(buf, pos)
            lst.append(v)
        return lst, pos
    # set
    if t == TYPE_SET:
        if pos+4 > len(buf):
            raise ValueError("Unexpected end of set length")
        n = struct.unpack('>I', buf[pos:pos+4])[0]
        pos += 4
        s = set()
        for _ in range(n):
            v, pos = _decode(buf, pos)
            s.add(v)
        return s, pos
    # dict
    if t == TYPE_DICT:
        if pos+4 > len(buf):
            raise ValueError("Unexpected end of dict length")
        n = struct.unpack('>I', buf[pos:pos+4])[0]
        pos += 4
        d = {}
        for _ in range(n):
            # key
            k, pos = _decode(buf, pos)
            if not isinstance(k, str):
                raise ValueError("Dict key not a string")
            v, pos = _decode(buf, pos)
            d[k] = v
        return d, pos
    raise ValueError(f"Unknown type code: {t}")

def _encode_with_schema(data, schema):
    """
    Encode a dict `data` according to `schema`.
    Schema is a dict mapping field names to type descriptors:
      - "int", "str", "bool", "dict"
      - ["int"], ["str"], ["bool"]
    """
    if not isinstance(schema, dict):
        raise TypeError("Schema must be a dict")
    if not isinstance(data, dict):
        raise TypeError("Data must be a dict when using schema")
    parts = []
    # number of fields
    num = len(schema)
    header = bytes([TYPE_SCHEMA, num])
    for field, descr in schema.items():
        # determine value or default
        if field in data:
            val = data[field]
            present = True
        else:
            present = False
        # validate and assign default if missing
        if isinstance(descr, str):
            if descr == 'int':
                if not present:
                    val = 0
                if not (isinstance(val, int) and not isinstance(val, bool)):
                    raise TypeError(f"Field '{field}' expected int")
            elif descr == 'str':
                if not present:
                    val = ""
                if not isinstance(val, str):
                    raise TypeError(f"Field '{field}' expected str")
            elif descr == 'bool':
                if not present:
                    val = False
                if not isinstance(val, bool):
                    raise TypeError(f"Field '{field}' expected bool")
            elif descr == 'dict':
                if not present:
                    val = {}
                if not isinstance(val, dict):
                    raise TypeError(f"Field '{field}' expected dict")
            else:
                raise TypeError(f"Unknown schema type: {descr}")
        elif isinstance(descr, list) and len(descr) == 1:
            eltype = descr[0]
            if not present:
                val = []
            if not isinstance(val, list):
                raise TypeError(f"Field '{field}' expected list")
            # check homogeneous and element type
            for e in val:
                if eltype == 'int':
                    if not (isinstance(e, int) and not isinstance(e, bool)):
                        raise TypeError(f"Field '{field}' list items must be int")
                elif eltype == 'str':
                    if not isinstance(e, str):
                        raise TypeError(f"Field '{field}' list items must be str")
                elif eltype == 'bool':
                    if not isinstance(e, bool):
                        raise TypeError(f"Field '{field}' list items must be bool")
                else:
                    raise TypeError(f"Unknown schema list element type: {eltype}")
        else:
            raise TypeError(f"Invalid schema descriptor for field '{field}'")
        # encode field name
        name_b = field.encode('utf-8')
        if len(name_b) > 255:
            raise ValueError("Field name too long")
        # encode value payload
        payload = _encode(val)
        parts.append(bytes([len(name_b)]) + name_b + struct.pack('>I', len(payload)) + payload)
    return header + b''.join(parts)
