from single_validation import SingleItemValidation

class BatchValidationInterface:
    def __init__(self):
        self.validator = SingleItemValidation()

    def validate_batch(self, records, schema):
        summary = {'valid': 0, 'invalid': 0, 'errors': {}}
        for rec in records:
            valid, errors = self.validator.validate(rec.copy(), schema)
            if valid:
                summary['valid'] += 1
            else:
                summary['invalid'] += 1
                for e in errors:
                    et = e.get('type')
                    summary['errors'].setdefault(et, 0)
                    summary['errors'][et] += 1
        return summary
