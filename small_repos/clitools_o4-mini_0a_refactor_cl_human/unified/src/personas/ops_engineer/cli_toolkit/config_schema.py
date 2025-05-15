"""
Schema generation for the CLI Toolkit.
"""
from typing import Any, Dict, List, Optional, Union

def generate_schema(config: dict, title: str = "CLI Toolkit Config") -> dict:
    """
    Generate a JSON schema from a configuration dictionary.
    
    Args:
        config: Configuration dictionary to generate schema from
        title: Schema title
        
    Returns:
        JSON schema as a dictionary
    """
    schema = {
        "type": "object",
        "title": title,
        "properties": {},
        "required": []
    }
    
    for key, value in config.items():
        # Add property to schema
        prop_schema = _generate_property_schema(key, value)
        schema["properties"][key] = prop_schema
        
        # Add to required list if not None
        if value is not None:
            schema["required"].append(key)
    
    return schema

def _generate_property_schema(key: str, value: Any) -> dict:
    """
    Generate schema for a property.
    
    Args:
        key: Property key
        value: Property value
        
    Returns:
        Property schema
    """
    if value is None:
        # Null value, could be any type
        return {}
    
    if isinstance(value, bool):
        return {"type": "boolean"}
    
    if isinstance(value, int):
        return {"type": "integer"}
    
    if isinstance(value, float):
        return {"type": "number"}
    
    if isinstance(value, str):
        return {"type": "string"}
    
    if isinstance(value, list):
        return _generate_array_schema(value)
    
    if isinstance(value, dict):
        return _generate_object_schema(value)
    
    # Default to string for unknown types
    return {"type": "string"}

def _generate_array_schema(array: List[Any]) -> dict:
    """
    Generate schema for an array.
    
    Args:
        array: Array value
        
    Returns:
        Array schema
    """
    schema = {"type": "array"}
    
    # If array is empty, we can't determine item type
    if not array:
        return schema
    
    # If all items are the same type, we can use that for the items schema
    item_types = set()
    item_schemas = []
    
    for item in array:
        if isinstance(item, bool):
            item_types.add("boolean")
            item_schemas.append({"type": "boolean"})
        elif isinstance(item, int):
            item_types.add("integer")
            item_schemas.append({"type": "integer"})
        elif isinstance(item, float):
            item_types.add("number")
            item_schemas.append({"type": "number"})
        elif isinstance(item, str):
            item_types.add("string")
            item_schemas.append({"type": "string"})
        elif isinstance(item, list):
            item_types.add("array")
            item_schemas.append(_generate_array_schema(item))
        elif isinstance(item, dict):
            item_types.add("object")
            item_schemas.append(_generate_object_schema(item))
        else:
            item_types.add("string")
            item_schemas.append({"type": "string"})
    
    # If all items are the same type, use a simple items schema
    if len(item_types) == 1:
        item_type = list(item_types)[0]
        schema["items"] = {"type": item_type}
        
        # For objects, add the properties schema if all items have the same structure
        if item_type == "object" and all(s.get("properties") == item_schemas[0].get("properties") for s in item_schemas):
            schema["items"] = item_schemas[0]
    else:
        # Use oneOf for mixed types
        schema["items"] = {"oneOf": list({str(s): s for s in item_schemas}.values())}
    
    return schema

def _generate_object_schema(obj: Dict[str, Any]) -> dict:
    """
    Generate schema for an object.
    
    Args:
        obj: Object value
        
    Returns:
        Object schema
    """
    schema = {"type": "object", "properties": {}, "required": []}
    
    for key, value in obj.items():
        # Add property to schema
        schema["properties"][key] = _generate_property_schema(key, value)
        
        # Add to required list if not None
        if value is not None:
            schema["required"].append(key)
    
    return schema

def merge_schemas(schemas: List[dict]) -> dict:
    """
    Merge multiple schemas into one.
    
    Args:
        schemas: List of schemas to merge
        
    Returns:
        Merged schema
    """
    if not schemas:
        return {}
    
    # Start with the first schema
    merged = schemas[0].copy()
    
    # Merge other schemas
    for schema in schemas[1:]:
        # Merge properties
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop in merged.get("properties", {}):
                # Property already exists, merge property schemas
                merged["properties"][prop] = _merge_property_schemas(
                    merged["properties"][prop],
                    prop_schema
                )
            else:
                # New property, add it
                if "properties" not in merged:
                    merged["properties"] = {}
                merged["properties"][prop] = prop_schema
        
        # Merge required lists
        if "required" in schema:
            if "required" not in merged:
                merged["required"] = []
            merged["required"] = list(set(merged["required"]) | set(schema["required"]))
    
    return merged

def _merge_property_schemas(schema1: dict, schema2: dict) -> dict:
    """
    Merge two property schemas.
    
    Args:
        schema1: First schema
        schema2: Second schema
        
    Returns:
        Merged schema
    """
    # If the types are different, use oneOf
    if schema1.get("type") != schema2.get("type"):
        return {"oneOf": [schema1, schema2]}
    
    # For the same type, merge appropriately
    if schema1.get("type") == "object":
        return {
            "type": "object",
            "properties": {
                **schema1.get("properties", {}),
                **schema2.get("properties", {})
            },
            "required": list(set(schema1.get("required", [])) | set(schema2.get("required", [])))
        }
    
    # For arrays, merge items schemas if possible
    if schema1.get("type") == "array":
        if not schema1.get("items") or not schema2.get("items"):
            return {"type": "array"}
        
        if schema1.get("items", {}).get("type") == schema2.get("items", {}).get("type"):
            return {
                "type": "array",
                "items": _merge_property_schemas(schema1["items"], schema2["items"])
            }
        
        return {
            "type": "array",
            "items": {"oneOf": [schema1.get("items", {}), schema2.get("items", {})]}
        }
    
    # For other types, just return the first schema
    return schema1


def gen_config_schema(definition: Dict[str, type]) -> Dict[str, Any]:
    """
    Generate a JSON schema from a configuration definition with types.
    
    Args:
        definition: Dictionary of configuration keys and their types
        
    Returns:
        JSON schema as a dictionary
    """
    schema = {
        "type": "object",
        "properties": {},
        "required": list(definition.keys())
    }
    
    for key, type_hint in definition.items():
        # Map Python types to JSON schema types
        if type_hint == str:
            schema["properties"][key] = {"type": "string"}
        elif type_hint == int:
            schema["properties"][key] = {"type": "integer"}
        elif type_hint == float:
            schema["properties"][key] = {"type": "number"}
        elif type_hint == bool:
            schema["properties"][key] = {"type": "boolean"}
        elif type_hint == list or type_hint == List:
            schema["properties"][key] = {"type": "array"}
        elif type_hint == dict or type_hint == Dict:
            schema["properties"][key] = {"type": "object"}
        else:
            # Default to string for unknown types
            schema["properties"][key] = {"type": "string"}
    
    return schema