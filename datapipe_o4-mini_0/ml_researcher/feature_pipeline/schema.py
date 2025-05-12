# try to use jsonschema if available, otherwise provide a minimal validator
try:
    import jsonschema

    def validate_schema(instance, schema):
        jsonschema.validate(instance=instance, schema=schema)
        return True
except ImportError:
    def validate_schema(instance, schema):
        """
        Minimal schema validation supporting:
          - type: object, array, string, number, boolean
          - required: [ ... ]
          - properties: { key: { type: ... } }
        Raises ValueError on mismatch.
        """
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "number": (int, float),
            "boolean": bool
        }
        # check root type
        expected_type = schema.get("type")
        if expected_type:
            py_type = type_map.get(expected_type)
            if py_type and not isinstance(instance, py_type):
                raise ValueError(f"Expected type {expected_type}, got {type(instance).__name__}")

        # check required fields
        required = schema.get("required", [])
        for field in required:
            if not isinstance(instance, dict) or field not in instance:
                raise ValueError(f"Missing required field: {field}")

        # check property types
        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if isinstance(instance, dict) and key in instance:
                expected = subschema.get("type")
                if expected:
                    py_type = type_map.get(expected)
                    if py_type and not isinstance(instance[key], py_type):
                        raise ValueError(f"Field '{key}' expected type {expected}, got {type(instance[key]).__name__}")

        return True
