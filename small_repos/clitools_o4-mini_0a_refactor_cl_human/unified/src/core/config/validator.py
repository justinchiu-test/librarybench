"""
Configuration validator module for CLI tools.
Validates configuration against schemas, supporting various schema formats.
"""

from typing import Any, Dict, List, Optional, Union, Callable


class ConfigValidator:
    """Validates configuration against schemas."""
    
    @staticmethod
    def validate(config: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """
        Validate configuration against a schema.
        
        Args:
            config: The configuration to validate
            schema: The schema to validate against
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        ConfigValidator._validate_obj(config, schema, '', errors)
        return errors
    
    @staticmethod
    def _validate_obj(obj: Any, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        """
        Recursively validate an object against a schema.
        
        Args:
            obj: The object to validate
            schema: The schema to validate against
            path: Current path in the object (for error messages)
            errors: List to collect error messages
        """
        obj_type = schema.get('type')
        if not obj_type:
            return
        
        # Check type
        if obj_type == 'object':
            if not isinstance(obj, dict):
                errors.append(f"{path}: expected object, got {type(obj).__name__}")
                return
            
            # Check required properties
            required = schema.get('required', [])
            for prop in required:
                if prop not in obj:
                    errors.append(f"{path}: missing required property '{prop}'")
            
            # Validate properties
            properties = schema.get('properties', {})
            for prop, prop_schema in properties.items():
                if prop in obj:
                    new_path = f"{path}.{prop}" if path else prop
                    ConfigValidator._validate_obj(obj[prop], prop_schema, new_path, errors)
            
            # Check for additional properties
            additional_props = schema.get('additionalProperties', True)
            if additional_props is False:
                for prop in obj:
                    if prop not in properties:
                        errors.append(f"{path}: property '{prop}' is not allowed")
        
        elif obj_type == 'array':
            if not isinstance(obj, list):
                errors.append(f"{path}: expected array, got {type(obj).__name__}")
                return
            
            # Check items
            items = schema.get('items')
            if items:
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    ConfigValidator._validate_obj(item, items, new_path, errors)
            
            # Check min/max items
            min_items = schema.get('minItems')
            if min_items is not None and len(obj) < min_items:
                errors.append(f"{path}: array must have at least {min_items} items")
            
            max_items = schema.get('maxItems')
            if max_items is not None and len(obj) > max_items:
                errors.append(f"{path}: array must have at most {max_items} items")
        
        elif obj_type == 'string':
            if not isinstance(obj, str):
                errors.append(f"{path}: expected string, got {type(obj).__name__}")
                return
            
            # Check min/max length
            min_length = schema.get('minLength')
            if min_length is not None and len(obj) < min_length:
                errors.append(f"{path}: string must be at least {min_length} characters")
            
            max_length = schema.get('maxLength')
            if max_length is not None and len(obj) > max_length:
                errors.append(f"{path}: string must be at most {max_length} characters")
            
            # Check pattern
            pattern = schema.get('pattern')
            if pattern:
                import re
                if not re.match(pattern, obj):
                    errors.append(f"{path}: string does not match pattern '{pattern}'")
        
        elif obj_type == 'number' or obj_type == 'integer':
            if obj_type == 'integer':
                if not isinstance(obj, int) or isinstance(obj, bool):
                    errors.append(f"{path}: expected integer, got {type(obj).__name__}")
                    return
            elif not isinstance(obj, (int, float)) or isinstance(obj, bool):
                errors.append(f"{path}: expected number, got {type(obj).__name__}")
                return
            
            # Check min/max
            minimum = schema.get('minimum')
            if minimum is not None and obj < minimum:
                errors.append(f"{path}: value must be at least {minimum}")
            
            maximum = schema.get('maximum')
            if maximum is not None and obj > maximum:
                errors.append(f"{path}: value must be at most {maximum}")
            
            # Check multiples
            multiple_of = schema.get('multipleOf')
            if multiple_of is not None:
                if obj % multiple_of != 0:
                    errors.append(f"{path}: value must be a multiple of {multiple_of}")
        
        elif obj_type == 'boolean':
            if not isinstance(obj, bool):
                errors.append(f"{path}: expected boolean, got {type(obj).__name__}")
                return
        
        elif obj_type == 'null':
            if obj is not None:
                errors.append(f"{path}: expected null, got {type(obj).__name__}")
                return


class JsonSchemaValidator:
    """Validator that uses jsonschema package if available."""
    
    @staticmethod
    def validate(config: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """
        Validate configuration using jsonschema.
        Falls back to ConfigValidator if jsonschema is not available.
        
        Args:
            config: The configuration to validate
            schema: The JSON Schema to validate against
            
        Returns:
            List of validation error messages (empty if valid)
        """
        try:
            import jsonschema
            
            try:
                jsonschema.validate(config, schema)
                return []
            except jsonschema.exceptions.ValidationError as e:
                return [str(e)]
            
        except ImportError:
            # Fall back to basic validator
            return ConfigValidator.validate(config, schema)