"""
Generate JSON schema from definitions.
"""
def gen_config_schema(definitions):
    if not isinstance(definitions, dict):
        raise ValueError("Definitions must be a dict")
    properties = {}
    required = []
    for key, schema in definitions.items():
        properties[key] = schema
        required.append(key)
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }