"""
Module: format_spec
Provides utilities to generate a detailed specification of a binary encoding format.
"""

from typing import Dict, Any, Union


def generate_format_specification(
    binary_format: Dict[str, Dict[str, Any]]
) -> str:
    """
    Generate a detailed, markdown-formatted specification of the binary format.

    Args:
        binary_format (dict): A mapping where each key is the field name (str),
            and each value is a dict with the following keys:
              - "type":    The data type as a string (e.g. "uint32", "bytes").
              - "size":    The size in bytes as an int, or a string like "remaining".
              - "description": A human-readable description of the field.

    Returns:
        str: A markdown-formatted table listing all fields with their type, size, and description.

    Raises:
        TypeError: If `binary_format` is not a dict, or any field spec is invalid.
    """
    if not isinstance(binary_format, dict):
        raise TypeError("binary_format must be a dict")

    # Header for markdown table
    lines = [
        "# Binary Format Specification",
        "",
        "Field | Type | Size (bytes) | Description",
        "--- | --- | --- | ---",
    ]

    for field_name, spec in binary_format.items():
        if not isinstance(field_name, str):
            raise TypeError(f"Field name must be a string, got {type(field_name)}")
        if not isinstance(spec, dict):
            raise TypeError(f"Spec for field '{field_name}' must be a dict, got {type(spec)}")

        # Extract and validate each part
        type_ = spec.get("type")
        size = spec.get("size")
        description = spec.get("description")

        if not isinstance(type_, str):
            raise TypeError(f"'type' for field '{field_name}' must be a string")
        if not (isinstance(size, (int, str))):
            raise TypeError(f"'size' for field '{field_name}' must be int or str")
        if not isinstance(description, str):
            raise TypeError(f"'description' for field '{field_name}' must be a string")

        lines.append(f"{field_name} | {type_} | {size} | {description}")

    return "\n".join(lines)
