def validate_schema(payload, schema):
    required = schema.get('required', [])
    for key in required:
        if key not in payload:
            raise ValueError(f"Missing required field: {key}")
    return True
