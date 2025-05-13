class OptionalFields:
    def apply_optional(self, data, schema):
        errors = []
        for field, props in schema.items():
            if not props.get('required', True) and field not in data:
                continue
            if props.get('required') and field not in data:
                errors.append({
                    'field': field,
                    'error': 'missing',
                    'level': props.get('error_level', 'error'),
                    'code': props.get('error_code')
                })
        return errors
