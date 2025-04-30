import json
import hashlib

def support_homogeneous_sets(data_set):
    """
    Ensure the provided data_set is a set and all its elements have the same type.
    Returns the common type, or None for an empty set.
    """
    if not isinstance(data_set, set):
        raise TypeError(f"support_homogeneous_sets expects a set, got {type(data_set).__name__}")
    types = {type(item) for item in data_set}
    if len(types) > 1:
        raise TypeError(f"Set has heterogeneous types: {types}")
    if not types:
        return None
    return types.pop()

def _encode(obj):
    """
    Internal recursive encoder: converts Python objects into JSON-serializable form,
    preserving set types via a custom marker.
    """
    if isinstance(obj, dict):
        return {k: _encode(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_encode(v) for v in obj]
    elif isinstance(obj, tuple):
        # tuples are serialized as lists
        return [_encode(v) for v in obj]
    elif isinstance(obj, set):
        # enforce homogeneous types
        item_type = support_homogeneous_sets(obj)
        return {
            "__type__": "set",
            "items": [_encode(v) for v in obj],
            "item_type": item_type.__name__ if item_type else None
        }
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        raise TypeError(f"Unsupported data type: {type(obj).__name__}")

def _decode(obj):
    """
    Internal recursive decoder: reconstructs Python objects from the JSON-serializable form.
    """
    if isinstance(obj, dict):
        if obj.get("__type__") == "set":
            # reconstruct set
            return set(_decode(v) for v in obj["items"])
        else:
            return {k: _decode(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_decode(v) for v in obj]
    else:
        # primitives
        return obj

def encode_nested_structures(data):
    """
    Encode a nested Python data structure into bytes, with an embedded checksum
    to ensure integrity.
    """
    # First convert the data into a JSON-safe structure
    payload = _encode(data)
    # Serialize payload deterministically
    data_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    # Compute checksum
    checksum = hashlib.sha256(data_json.encode("utf-8")).hexdigest()
    # Build envelope
    envelope = {"data": payload, "checksum": checksum}
    return json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def decode_nested_structures(encoded_bytes):
    """
    Decode the bytes produced by encode_nested_structures back into the original
    Python data structure. Raises ValueError if integrity check fails.
    """
    if isinstance(encoded_bytes, bytes):
        text = encoded_bytes.decode("utf-8")
    else:
        text = encoded_bytes
    # Parse envelope
    envelope = json.loads(text)
    # Integrity check
    if not check_data_integrity(text):
        raise ValueError("Data integrity check failed.")
    # Reconstruct data
    return _decode(envelope["data"])

def check_data_integrity(encoded_bytes):
    """
    Check the SHA-256 checksum embedded in the encoded data. Returns True if
    the data is intact, False otherwise.
    """
    if isinstance(encoded_bytes, bytes):
        text = encoded_bytes.decode("utf-8")
    else:
        text = encoded_bytes
    try:
        envelope = json.loads(text)
        payload = envelope["data"]
        old_checksum = envelope["checksum"]
    except Exception:
        return False
    # Re-serialize payload deterministically
    data_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    new_checksum = hashlib.sha256(data_json.encode("utf-8")).hexdigest()
    return new_checksum == old_checksum

def validate_schema(data, schema):
    """
    Validate that 'data' conforms to 'schema'. Raises:
      - TypeError for type mismatches
      - KeyError for missing or extra dict keys
      - ValueError for malformed schemas
    Returns True if validation passes.
    """
    def _validate(obj, sch, path):
        # Primitive type schema
        if isinstance(sch, type):
            if not isinstance(obj, sch):
                raise TypeError(f"Expected type {sch.__name__} at {path}, got {type(obj).__name__}")
        # List schema
        elif isinstance(sch, list):
            if len(sch) != 1:
                raise ValueError(f"Schema list at {path} must have exactly one element")
            if not isinstance(obj, list):
                raise TypeError(f"Expected list at {path}, got {type(obj).__name__}")
            for idx, item in enumerate(obj):
                _validate(item, sch[0], f"{path}[{idx}]")
        # Tuple schema (treated like list)
        elif isinstance(sch, tuple):
            if len(sch) != 1:
                raise ValueError(f"Schema tuple at {path} must have exactly one element")
            if not isinstance(obj, list):
                raise TypeError(f"Expected list (for tuple) at {path}, got {type(obj).__name__}")
            for idx, item in enumerate(obj):
                _validate(item, sch[0], f"{path}[{idx}]")
        # Dict schema
        elif isinstance(sch, dict):
            # Set schema: special single-key dict {"set": ...}
            if set(sch.keys()) == {"set"}:
                sub_sch = sch["set"]
                if not isinstance(obj, set):
                    raise TypeError(f"Expected set at {path}, got {type(obj).__name__}")
                for item in obj:
                    _validate(item, sub_sch, f"{path}{{item}}")
            else:
                # Regular dict schema
                if not isinstance(obj, dict):
                    raise TypeError(f"Expected dict at {path}, got {type(obj).__name__}")
                # Check key sets match exactly
                obj_keys = set(obj.keys())
                sch_keys = set(sch.keys())
                missing = sch_keys - obj_keys
                extra = obj_keys - sch_keys
                if missing or extra:
                    msgs = []
                    if missing:
                        msgs.append(f"missing keys {missing}")
                    if extra:
                        msgs.append(f"unexpected keys {extra}")
                    raise KeyError(f"Key mismatch at {path}: {', '.join(msgs)}")
                for key in sch_keys:
                    _validate(obj[key], sch[key], f"{path}.{key}")
        else:
            raise TypeError(f"Invalid schema type at {path}: {sch}")
    _validate(data, schema, "root")
    return True
