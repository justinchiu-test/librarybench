# json_schema_support
import jsonschema

def export_schema(definition: dict) -> dict:
    """
    Return the JSON Schema for the given definition.
    Here we assume definition is already a valid schema.
    """
    return definition

def validate_schema(data: dict, schema: dict) -> None:
    """
    Validate data against the given JSON Schema.
    Raises jsonschema.ValidationError on failure.
    """
    jsonschema.validate(instance=data, schema=schema)
