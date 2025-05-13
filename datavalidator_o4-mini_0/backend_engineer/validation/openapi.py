def generate_openapi_schema(schema, title="Schema"):
    properties = {}
    required = []
    for name, field in schema.fields.items():
        key = field.alias or name
        t = field.type_
        if t is int:
            tp = "integer"
        elif t is float:
            tp = "number"
        elif t is bool:
            tp = "boolean"
        else:
            tp = "string"
        prop = {"type": tp}
        if field.default is not None:
            prop["default"] = field.default
        properties[key] = prop
        if field.required:
            required.append(key)
    return {
        "openapi": "3.0.0",
        "info": {"title": title, "version": "1.0.0"},
        "components": {
            "schemas": {
                title: {"type": "object", "properties": properties, "required": required}
            }
        },
    }
