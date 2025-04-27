import struct
import zlib
import gzip
import lzma

# Type tags
TAG_INT = 0x01
TAG_STR = 0x02
TAG_BOOL = 0x03
TAG_LIST = 0x04
TAG_SET = 0x05
TAG_DICT = 0x06
TAG_SCHEMA = 0x07
TAG_SCHEMA_DATA = 0x08
TAG_COMPRESSED = 0x09

# Compression algorithm codes
ALGO_ZLIB = 1
ALGO_GZIP = 2
ALGO_LZMA = 3

# Minimum size to attempt compression
_COMPRESSION_THRESHOLD = 100

# Schema element spec bits
# high bit (0x80) set => list of base type
# low 7 bits => base type code


def encode(obj, schema=None, compress=False, compression_algorithm="zlib"):
    """
    Main encode function.
    """
    if schema is not None:
        if not isinstance(obj, dict):
            raise TypeError("Data must be dict when schema is provided")
        # Build schema metadata
        fields = []
        for name, spec in schema.items():
            # name must be string
            if not isinstance(name, str):
                raise TypeError("Schema field names must be strings")
            # Determine type code
            if isinstance(spec, list):
                if len(spec) != 1 or not isinstance(spec[0], str):
                    raise TypeError("Schema list spec must be single-element list of type string")
                base = _type_name_to_code(spec[0])
                type_byte = base | 0x80
            else:
                if not isinstance(spec, str):
                    raise TypeError("Schema spec must be string or single-element list")
                base = _type_name_to_code(spec)
                type_byte = base
            fields.append((name, type_byte))
        # Build schema metadata bytes
        meta = struct.pack(">I", len(fields))
        for name, type_byte in fields:
            name_b = name.encode("utf-8")
            meta += struct.pack(">H", len(name_b)) + name_b
            meta += struct.pack("B", type_byte)
        # Build payload for schema data
        payload = b""
        for name, type_byte in fields:
            if name in obj:
                val = obj[name]
            else:
                # default values
                val = _default_for_type_byte(type_byte)
            # Validate type
            _validate_type(val, type_byte)
            payload += _encode_element(val)
        # Wrap with schema tag
        encoded = struct.pack("B", TAG_SCHEMA) + meta + struct.pack("B", TAG_SCHEMA_DATA) + payload
    else:
        encoded = _encode_element(obj)

    # Handle compression
    if compress:
        if len(encoded) > _COMPRESSION_THRESHOLD:
            algo = compression_algorithm.lower() if compression_algorithm else "zlib"
            if algo == "zlib":
                code = ALGO_ZLIB
                comp = zlib.compress(encoded)
            elif algo == "gzip":
                code = ALGO_GZIP
                comp = gzip.compress(encoded)
            elif algo == "lzma":
                code = ALGO_LZMA
                comp = lzma.compress(encoded)
            else:
                raise ValueError(f"Unknown compression algorithm: {compression_algorithm}")
            header = struct.pack("B", TAG_COMPRESSED)
            header += struct.pack("B", code)
            header += struct.pack(">I", len(comp))
            return header + comp
        # else skip compression for small data
    return encoded


def decode(data: bytes, field=None):
    """
    Main decode function. If field is provided, extract only that field (schema only).
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("decode requires bytes input")

    pos = 0
    length = len(data)

    # Handle compressed top-level
    if length >= 1 and data[0] == TAG_COMPRESSED:
        if length < 6:
            raise ValueError("Invalid compressed data")
        algo_code = data[1]
        comp_len = struct.unpack(">I", data[2:6])[0]
        comp = data[6:6+comp_len]
        if len(comp) != comp_len:
            raise ValueError("Invalid compressed data length")
        if algo_code == ALGO_ZLIB:
            data = zlib.decompress(comp)
        elif algo_code == ALGO_GZIP:
            data = gzip.decompress(comp)
        elif algo_code == ALGO_LZMA:
            data = lzma.decompress(comp)
        else:
            raise ValueError("Unknown compression code")
        pos = 0
        length = len(data)

    # Handle schema-wrapped
    if length >= 1 and data[pos] == TAG_SCHEMA:
        pos += 1
        # read schema metadata
        if pos + 4 > length:
            raise ValueError("Invalid schema metadata")
        n_fields = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        fields = []
        for _ in range(n_fields):
            if pos + 2 > length:
                raise ValueError("Invalid schema field")
            name_len = struct.unpack(">H", data[pos:pos+2])[0]
            pos += 2
            if pos + name_len > length:
                raise ValueError("Invalid schema field name")
            name = data[pos:pos+name_len].decode("utf-8")
            pos += name_len
            if pos >= length:
                raise ValueError("Invalid schema field type")
            type_byte = data[pos]
            pos += 1
            fields.append((name, type_byte))
        # expect schema data tag
        if pos >= length or data[pos] != TAG_SCHEMA_DATA:
            raise ValueError("Missing schema data tag")
        pos += 1
        # if field-level
        if field is not None:
            # find index
            idx = None
            for i, (n, _) in enumerate(fields):
                if n == field:
                    idx = i
                    break
            if idx is None:
                raise ValueError(f"Field {field} not in schema")
            # skip elements until idx
            for i in range(idx):
                pos = _skip_element(data, pos)
            # decode target element
            val, _ = _decode_element(data, pos)
            return val
        else:
            # decode all into dict
            result = {}
            for name, _ in fields:
                val, newpos = _decode_element(data, pos)
                result[name] = val
                pos = newpos
            return result

    # Non-schema decode
    if field is not None:
        raise ValueError("Field-level decode requires schema")
    val, final_pos = _decode_element(data, 0)
    return val


def _encode_with_schema(obj, schema):
    # Provided for tests, but real work done in encode()
    return encode(obj, schema=schema)


def _type_name_to_code(name: str) -> int:
    if name == "int":
        return TAG_INT
    elif name == "str":
        return TAG_STR
    elif name == "bool":
        return TAG_BOOL
    elif name == "list":
        return TAG_LIST
    elif name == "set":
        return TAG_SET
    elif name == "dict":
        return TAG_DICT
    else:
        raise TypeError(f"Unsupported schema type name: {name}")


def _default_for_type_byte(type_byte: int):
    base = type_byte & 0x7F
    is_list = (type_byte & 0x80) != 0
    if is_list:
        return []
    if base == TAG_INT:
        return 0
    elif base == TAG_STR:
        return ""
    elif base == TAG_BOOL:
        return False
    elif base == TAG_LIST:
        return []
    elif base == TAG_SET:
        return set()
    elif base == TAG_DICT:
        return {}
    else:
        raise TypeError("Unsupported type in schema default")


def _validate_type(val, type_byte):
    base = type_byte & 0x7F
    is_list = (type_byte & 0x80) != 0
    if is_list:
        if not isinstance(val, list):
            raise TypeError("Expected list for schema field")
        # homogeneous
        for item in val:
            if not _check_base_type(item, base):
                raise TypeError("List item type does not match schema")
    else:
        if not _check_base_type(val, base):
            raise TypeError("Value type does not match schema")


def _check_base_type(val, base):
    if base == TAG_INT:
        return isinstance(val, int) and not isinstance(val, bool)
    if base == TAG_STR:
        return isinstance(val, str)
    if base == TAG_BOOL:
        return isinstance(val, bool)
    if base == TAG_LIST:
        return isinstance(val, list)
    if base == TAG_SET:
        return isinstance(val, set)
    if base == TAG_DICT:
        return isinstance(val, dict)
    return False


def _encode_element(obj):
    # Dispatch by type
    # int (not bool)
    if isinstance(obj, bool):
        # must come before int because bool is subclass
        b = b'\x01' if obj else b'\x00'
        return struct.pack("B", TAG_BOOL) + b
    if isinstance(obj, int):
        # exclude bool
        b = struct.pack(">q", obj)
        return struct.pack("B", TAG_INT) + b
    if isinstance(obj, str):
        b = obj.encode("utf-8")
        return struct.pack("B", TAG_STR) + struct.pack(">I", len(b)) + b
    if isinstance(obj, list):
        # homogeneous
        if len(obj) > 0:
            first_tag = _infer_tag(obj[0])
            for item in obj:
                if _infer_tag(item) != first_tag:
                    raise TypeError("Non-homogeneous list")
        res = struct.pack("B", TAG_LIST) + struct.pack(">I", len(obj))
        for item in obj:
            res += _encode_element(item)
        return res
    if isinstance(obj, set):
        # homogeneous
        lst = list(obj)
        if len(lst) > 0:
            first_tag = _infer_tag(lst[0])
            for item in lst:
                if _infer_tag(item) != first_tag:
                    raise TypeError("Non-homogeneous set")
        res = struct.pack("B", TAG_SET) + struct.pack(">I", len(lst))
        for item in lst:
            res += _encode_element(item)
        return res
    if isinstance(obj, dict):
        res = struct.pack("B", TAG_DICT) + struct.pack(">I", len(obj))
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError("Dictionary keys must be strings")
            res += _encode_element(k)
            res += _encode_element(v)
        return res
    raise TypeError(f"Unsupported type: {type(obj)}")


def _infer_tag(obj):
    if isinstance(obj, bool):
        return TAG_BOOL
    if isinstance(obj, int):
        return TAG_INT
    if isinstance(obj, str):
        return TAG_STR
    if isinstance(obj, list):
        return TAG_LIST
    if isinstance(obj, set):
        return TAG_SET
    if isinstance(obj, dict):
        return TAG_DICT
    raise TypeError("Unsupported type in inference")


def _decode_element(data: bytes, pos: int):
    if pos >= len(data):
        raise ValueError("Unexpected end of data")
    tag = data[pos]
    pos += 1
    # INT
    if tag == TAG_INT:
        if pos + 8 > len(data):
            raise ValueError("Truncated int")
        val = struct.unpack(">q", data[pos:pos+8])[0]
        return val, pos + 8
    # STR
    if tag == TAG_STR:
        if pos + 4 > len(data):
            raise ValueError("Truncated str length")
        l = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        if pos + l > len(data):
            raise ValueError("Truncated str data")
        val = data[pos:pos+l].decode("utf-8")
        return val, pos + l
    # BOOL
    if tag == TAG_BOOL:
        if pos >= len(data):
            raise ValueError("Truncated bool")
        b = data[pos]
        if b == 0:
            return False, pos+1
        elif b == 1:
            return True, pos+1
        else:
            raise ValueError("Invalid bool value")
    # LIST
    if tag == TAG_LIST:
        if pos + 4 > len(data):
            raise ValueError("Truncated list length")
        cnt = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        lst = []
        for _ in range(cnt):
            v, pos = _decode_element(data, pos)
            lst.append(v)
        return lst, pos
    # SET
    if tag == TAG_SET:
        if pos + 4 > len(data):
            raise ValueError("Truncated set length")
        cnt = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        s = set()
        for _ in range(cnt):
            v, pos = _decode_element(data, pos)
            s.add(v)
        return s, pos
    # DICT
    if tag == TAG_DICT:
        if pos + 4 > len(data):
            raise ValueError("Truncated dict length")
        cnt = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        d = {}
        for _ in range(cnt):
            key, pos = _decode_element(data, pos)
            val, pos = _decode_element(data, pos)
            d[key] = val
        return d, pos
    raise ValueError(f"Invalid type header: 0x{tag:02x}")


def _skip_element(data: bytes, pos: int):
    """
    Advances pos past the element at pos, returns new pos.
    """
    if pos >= len(data):
        raise ValueError("Unexpected end during skip")
    tag = data[pos]
    pos += 1
    # INT
    if tag == TAG_INT:
        return pos + 8
    if tag == TAG_BOOL:
        return pos + 1
    if tag == TAG_STR:
        if pos + 4 > len(data):
            raise ValueError("Truncated str length")
        l = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        return pos + l
    if tag == TAG_LIST or tag == TAG_SET:
        if pos + 4 > len(data):
            raise ValueError("Truncated list/set length")
        cnt = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        for _ in range(cnt):
            pos = _skip_element(data, pos)
        return pos
    if tag == TAG_DICT:
        if pos + 4 > len(data):
            raise ValueError("Truncated dict length")
        cnt = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        for _ in range(cnt):
            pos = _skip_element(data, pos)
            pos = _skip_element(data, pos)
        return pos
    # Should not encounter schema or compressed here
    raise ValueError(f"Cannot skip unknown tag: {tag}")
