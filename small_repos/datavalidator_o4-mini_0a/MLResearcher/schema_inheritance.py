def extend_schema(base_schema, overrides):
    merged = {}
    for k, v in base_schema.items():
        merged[k] = v.copy() if isinstance(v, dict) else v
    for k, v in overrides.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = {**merged[k], **v}
        else:
            merged[k] = v
    return merged
