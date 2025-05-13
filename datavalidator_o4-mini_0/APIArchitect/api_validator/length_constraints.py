class LengthConstraints:
    def validate_length(self, data, schema):
        errors = []
        for field, props in schema.items():
            max_len = props.get('max_length')
            if max_len is not None and field in data and isinstance(data[field], str):
                if len(data[field]) > max_len:
                    errors.append({
                        'field': field,
                        'error': 'max_length',
                        'code': props.get('error_code')
                    })
        return errors
