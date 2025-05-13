def make_optional(schema, field):
    if field in schema and isinstance(schema[field], dict):
        schema[field]['optional'] = True
    return schema

def is_optional(props):
    return props.get('optional', False)
