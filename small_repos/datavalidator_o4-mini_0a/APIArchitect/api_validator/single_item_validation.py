class SingleItemValidation:
    def validate_item(self, data, schema):
        errors = []
        valid = True
        for field, props in schema.items():
            if props.get('required') and field not in data:
                errors.append({
                    'field': field,
                    'error': 'required',
                    'code': props.get('error_code')
                })
                valid = False
                continue
            if field in data:
                expected = props.get('type')
                if expected and not isinstance(data[field], expected):
                    errors.append({
                        'field': field,
                        'error': 'type',
                        'code': props.get('error_code')
                    })
                    valid = False
                max_len = props.get('max_length')
                if max_len is not None and isinstance(data[field], str) and len(data[field]) > max_len:
                    errors.append({
                        'field': field,
                        'error': 'max_length',
                        'code': props.get('error_code')
                    })
                    valid = False
        return {'valid': valid, 'errors': errors}
