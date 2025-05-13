import json

def export_schema(schema, file_path, format='json'):
    with open(file_path, 'w') as f:
        if format == 'json':
            json.dump(schema, f)
        elif format == 'yaml':
            # Fallback to JSON format for YAML output to avoid external deps
            json.dump(schema, f)
        else:
            raise ValueError('Unsupported format')

def load_schema(file_path):
    with open(file_path) as f:
        if file_path.endswith('.json'):
            return json.load(f)
        elif file_path.endswith(('.yml', '.yaml')):
            # Fallback to JSON loader for YAML files
            return json.load(f)
        else:
            raise ValueError('Unsupported file type')
