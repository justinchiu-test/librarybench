"""
Generate JSON schema for configuration definitions.
"""
def gen_config_schema(defs):
    # defs: dict of key -> { 'type': <type> }
    schema = {
        "type": "object",
        "properties": defs,
        "required": list(defs.keys()),
    }
    return schema