"""Validation utilities for configuration values."""
import re
from typing import Dict, Any, List, Optional, Union, Type, Callable

try:
    import jsonschema
except ImportError:
    jsonschema = None


class TypeValidator:
    """Utility class for validating configuration types."""
    
    # Map of special type names to validation functions
    _special_types = {
        'ip': lambda v: re.match(r'^(\d{1,3}\.){3}\d{1,3}$', str(v)) is not None,
        'port': lambda v: isinstance(v, int) and 0 <= v <= 65535,
        'bool': lambda v: isinstance(v, bool) or (isinstance(v, str) and 
                                                v.lower() in ('true', 'false', 'yes', 'no', '1', '0')),
        'email': lambda v: re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', str(v)) is not None,
        'url': lambda v: re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w%!$&\'()*+,;=:]+)*$', str(v)) is not None,
        'token': lambda v: re.match(r'^[a-zA-Z0-9_-]+$', str(v)) is not None,
    }
    
    @classmethod
    def validate_type(cls, 
                     value: Any, 
                     expected_type: Union[Type, str], 
                     key: str,
                     path: Optional[str] = None,
                     filename: Optional[str] = None) -> bool:
        """Validate that a value is of the expected type.
        
        Args:
            value: The value to validate
            expected_type: The expected type
            key: The configuration key
            path: Optional path to the value in the configuration 
            filename: Optional configuration filename
            
        Returns:
            True if the value is of the expected type
            
        Raises:
            ValidationError: If the value is not of the expected type
        """
        from .errors import ValidationError
        
        # Handle special types
        if isinstance(expected_type, str):
            type_name = expected_type.lower()
            
            if type_name in cls._special_types:
                if not cls._special_types[type_name](value):
                    raise ValidationError(
                        file=filename,
                        key=key,
                        path=path,
                        expected=type_name,
                        actual=type(value).__name__,
                        message=f"Expected '{key}' to be a valid {type_name}"
                    )
                return True
                
            # Try to convert string type names to Python types
            try:
                expected_type = {
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'none': type(None)
                }.get(type_name)
                
                if expected_type is None:
                    raise ValidationError(
                        file=filename,
                        key=key,
                        path=path,
                        expected=type_name,
                        actual=type(value).__name__,
                        message=f"Unknown type '{type_name}' for key '{key}'"
                    )
            except KeyError:
                raise ValidationError(
                    file=filename,
                    key=key,
                    path=path,
                    expected=type_name,
                    actual=type(value).__name__,
                    message=f"Unknown type '{type_name}' for key '{key}'"
                )
                
        # Handle regular Python types
        if not isinstance(value, expected_type):
            # Special handling for some types
            if expected_type == bool and isinstance(value, str):
                if value.lower() in ('true', 'false', 'yes', 'no', '1', '0'):
                    return True
                    
            if expected_type == int and isinstance(value, str):
                try:
                    int(value)
                    return True
                except ValueError:
                    pass
                    
            if expected_type == float and isinstance(value, str):
                try:
                    float(value)
                    return True
                except ValueError:
                    pass
                    
            # Type validation failed
            raise ValidationError(
                file=filename,
                key=key,
                path=path,
                expected=expected_type.__name__,
                actual=type(value).__name__,
                message=f"Expected '{key}' to be of type {expected_type.__name__}, got {type(value).__name__}"
            )
            
        return True


def validate_types(config: Dict[str, Any], 
                  schema: Dict[str, Union[Type, str]], 
                  filename: Optional[str] = None) -> bool:
    """Validate that all values in a configuration match their expected types.
    
    Args:
        config: The configuration to validate
        schema: The schema mapping keys to expected types
        filename: Optional configuration filename
        
    Returns:
        True if all values match their expected types
        
    Raises:
        ValidationError: If any value does not match its expected type
    """
    for key, expected_type in schema.items():
        if key in config:
            TypeValidator.validate_type(config[key], expected_type, key, filename=filename)
            
    return True


def validate_with_jsonschema(config: Dict[str, Any], 
                            schema: Dict[str, Any],
                            filename: Optional[str] = None) -> bool:
    """Validate a configuration against a JSON schema.
    
    Args:
        config: The configuration to validate
        schema: The JSON schema
        filename: Optional configuration filename
        
    Returns:
        True if the configuration is valid
        
    Raises:
        ValidationError: If the configuration is invalid
        RuntimeError: If jsonschema is not available
    """
    from .errors import ValidationError
    
    if jsonschema is None:
        raise RuntimeError(
            "jsonschema is not installed. Please install it with: pip install jsonschema"
        )
        
    try:
        jsonschema.validate(instance=config, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        path = ".".join(str(p) for p in e.path) if e.path else None
        raise ValidationError(
            file=filename,
            path=path,
            key=e.path[-1] if e.path else None,
            message=e.message,
            expected=None,
            actual=None
        )