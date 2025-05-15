"""
JSON schema generation from configuration data.
"""

def infer_schema(obj):
    """
    Infer a JSON schema dictionary from a Python object.
    """
    # Object (dict)
    if isinstance(obj, dict):
        props = {k: infer_schema(v) for k, v in obj.items()}
        return {"type": "object", "properties": props}
    # Array (list)
    if isinstance(obj, list):
        schema = {"type": "array"}
        if obj:
            schema["items"] = infer_schema(obj[0])
        return schema
    # Primitive types
    if obj is None:
        t = "null"
    elif isinstance(obj, bool):
        t = "boolean"
    elif isinstance(obj, int) and not isinstance(obj, bool):
        t = "integer"
    elif isinstance(obj, float):
        t = "number"
    else:
        t = "string"
    return {"type": t}

def export_json_schema(cfg_or_path):
    """
    Generate a JSON schema dict from a config dict or file path or ConfigManager.
    """
    # Lazy import to avoid circular
    from .loader import load_config

    data = None
    # Determine source
    if isinstance(cfg_or_path, str):
        mgr = load_config(cfg_or_path)
        data = mgr._config  # internal dict
    elif hasattr(cfg_or_path, '_config'):
        data = cfg_or_path._config
    elif isinstance(cfg_or_path, dict):
        data = cfg_or_path
    else:
        raise ValueError("Unsupported type for export_json_schema")
    # Build schema
    schema = infer_schema(data)
    # Attach defaults where applicable
    def _attach_defaults(sch, obj):
        if sch.get("type") == "object" and isinstance(obj, dict):
            for k, v in obj.items():
                prop = sch.get("properties", {}).get(k)
                if prop is not None:
                    prop["default"] = v
                    _attach_defaults(prop, v)
        if sch.get("type") == "array" and isinstance(obj, list) and sch.get("items"):
            # default only applies to object items
            _attach_defaults(sch["items"], obj[0])
    _attach_defaults(schema, data)
    return schema