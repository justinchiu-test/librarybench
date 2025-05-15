"""
Validation functions for configuration data.
"""
from .error import ValidationError

def validate_types(*args, filename=None):
    """
    Overloaded function:
    - validate_types(cfg: dict, schema: dict, filename: str=None) -> True or raises ValidationError
    - validate_types(key: str, value: Any, expected_type: type) -> True or raises ValidationError
    """
    # Dictionary & schema mapping to types
    if args and isinstance(args[0], dict) and len(args) >= 2 and isinstance(args[1], dict):
        cfg = args[0]
        schema = args[1]
        for key, expected in schema.items():
            if key not in cfg:
                continue
            actual_val = cfg[key]
            if not isinstance(actual_val, expected):
                raise ValidationError(
                    file=filename,
                    key=key,
                    message=f"expected {expected.__name__}",
                    expected=expected.__name__,
                    actual=type(actual_val).__name__
                )
        return True
    # Single value validation
    if len(args) == 3 and isinstance(args[0], str):
        name, value, expected = args
        if not isinstance(value, expected):
            raise ValidationError(
                key=name,
                message=f"expected {expected.__name__}",
                expected=expected.__name__,
                actual=type(value).__name__
            )
        return True
    raise ValueError("Invalid arguments to validate_types")