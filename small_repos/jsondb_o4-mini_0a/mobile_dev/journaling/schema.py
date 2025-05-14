import time

class SchemaError(Exception):
    pass

def validate_entry(entry):
    required_fields = ['id', 'content', 'tags', 'attachments', 'metadata', 'created_at', 'updated_at']
    if not isinstance(entry, dict):
        raise SchemaError('Entry must be a dict')
    for field in required_fields:
        if field not in entry:
            raise SchemaError(f'Missing field: {field}')
    if not isinstance(entry['id'], str):
        raise SchemaError('id must be a string')
    if not isinstance(entry['content'], str):
        raise SchemaError('content must be a string')
    if not isinstance(entry['tags'], list) or not all(isinstance(t, str) for t in entry['tags']):
        raise SchemaError('tags must be a list of strings')
    if not isinstance(entry['attachments'], list) or not all(isinstance(a, str) for a in entry['attachments']):
        raise SchemaError('attachments must be a list of strings')
    if not isinstance(entry['metadata'], dict):
        raise SchemaError('metadata must be a dict')
    for time_field in ['created_at', 'updated_at']:
        if not isinstance(entry[time_field], (int, float)):
            raise SchemaError(f'{time_field} must be a timestamp')
    if entry['created_at'] > entry['updated_at']:
        raise SchemaError('created_at cannot be after updated_at')
    if 'deleted' in entry and not isinstance(entry['deleted'], bool):
        raise SchemaError('deleted must be a boolean')
    if 'deleted_at' in entry and not isinstance(entry['deleted_at'], (int, float)):
        raise SchemaError('deleted_at must be a timestamp')
