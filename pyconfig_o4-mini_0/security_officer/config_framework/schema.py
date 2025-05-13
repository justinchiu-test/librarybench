def export_schema(config):
    type_map = {
        str: "string",
        int: "integer",
        bool: "boolean",
        list: "array",
        dict: "object",
        float: "number",
    }
    schema = {"type": "object", "properties": {}}
    for key, value in config.items():
        t = type_map.get(type(value), "string")
        schema["properties"][key] = {"type": t}
    return schema
