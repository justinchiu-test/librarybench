def validate_schema(data, schema):
    """
    schema for JSON: {'properties': {'key': type, ...}}
    schema for binary: {'length': int}
    """
    if isinstance(data, dict):
        props = schema.get('properties', {})
        for key, typ in props.items():
            if key not in data:
                raise ValueError(f"Missing key {key}")
            if not isinstance(data[key], typ):
                raise TypeError(f"Key {key} expected {typ}")
        return True
    elif isinstance(data, (bytes, bytearray)):
        length = schema.get('length')
        if length is None or len(data) != length:
            raise ValueError("Invalid binary length")
        return True
    else:
        raise TypeError("Unsupported data type")
