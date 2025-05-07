from utils import validate_type

def generate_format_specification(
    binary_format: dict
) -> str:
    validate_type(binary_format, dict, 'binary_format')
    lines = [
        "# Binary Format Specification",
        "",
        "Field | Type | Size (bytes) | Description",
        "--- | --- | --- | ---",
    ]
    for field_name, spec in binary_format.items():
        validate_type(field_name, str, 'field name')
        validate_type(spec, dict, f"spec for field '{field_name}'")
        type_ = spec.get("type")
        size = spec.get("size")
        description = spec.get("description")
        validate_type(type_, str, f"'type' for field '{field_name}'")
        if not isinstance(size, (int, str)):
            raise TypeError(f"'size' for field '{field_name}' must be int or str")
        validate_type(description, str, f"'description' for field '{field_name}'")
        lines.append(f"{field_name} | {type_} | {size} | {description}")
    return "\n".join(lines)
