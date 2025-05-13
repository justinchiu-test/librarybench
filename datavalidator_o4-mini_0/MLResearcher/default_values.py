def set_default_values(record, schema):
    for field, props in schema.items():
        if 'default' in props and record.get(field) is None:
            record[field] = props['default']
    return record
