class SingleItemValidation:
    def validate(self, record, schema):
        errors = []
        for field, props in schema.items():
            val = record.get(field)
            if val is None:
                if not props.get('optional', False):
                    errors.append({'field': field, 'type': 'missing'})
                continue
            expected_type = props.get('type')
            if expected_type and not isinstance(val, expected_type):
                errors.append({'field': field, 'type': 'invalid'})
                continue
            if isinstance(val, (int, float)):
                if 'min' in props and val < props['min']:
                    errors.append({'field': field, 'type': 'outlier'})
                if 'max' in props and val > props['max']:
                    errors.append({'field': field, 'type': 'outlier'})
            if 'length' in props:
                if not hasattr(val, '__len__') or len(val) != props['length']:
                    errors.append({'field': field, 'type': 'length'})
        return (len(errors) == 0), errors
