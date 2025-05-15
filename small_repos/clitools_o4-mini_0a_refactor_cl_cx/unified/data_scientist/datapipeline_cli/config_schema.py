def generate_schema(fields):
    """
    Generate a schema based on type annotations
    
    Args:
        fields: Dictionary of field names to type objects
        
    Returns:
        dict: Schema representing the types
    """
    schema = {}
    
    type_mapping = {
        int: 'integer',
        str: 'string',
        bool: 'boolean',
        list: 'list',
        dict: 'dict',
        float: 'float'
    }
    
    for field_name, field_type in fields.items():
        schema[field_name] = {
            'type': type_mapping.get(field_type, 'unknown')
        }
        
    return schema