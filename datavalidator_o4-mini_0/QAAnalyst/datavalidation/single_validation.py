from .error_codes import ErrorCodeSupport

class SingleItemValidation:
    def __init__(self, schema, length_constraints=None, optional_fields=None, conditional_validation=None):
        self.schema = schema
        self.error_support = ErrorCodeSupport()
        self.length_constraints = length_constraints
        self.optional_fields = optional_fields
        self.conditional = conditional_validation

    def validate_single(self, record, scenario=None):
        errors = []
        # Check required fields
        for field in self.schema.get('required', []):
            if field not in record or record[field] is None:
                errors.append({
                    'field': field,
                    'error': 'missing_field',
                    'code': self.error_support.get_error_code('missing_field')
                })
        # Check length constraints
        if self.length_constraints:
            for violation in self.length_constraints.check_length(record):
                errors.append({
                    'field': violation['field'],
                    'error': 'length_exceeded',
                    'code': self.error_support.get_error_code('length_exceeded')
                })
        # Check optional fields in strict mode
        if self.optional_fields:
            for violation in self.optional_fields.check_optional(record):
                errors.append({
                    'field': violation['field'],
                    'error': 'optional_missing',
                    'code': self.error_support.get_error_code('optional_missing')
                })
        # Check conditional validations
        if self.conditional and scenario:
            for violation in self.conditional.validate(record, scenario):
                errors.append({
                    'field': violation['field'],
                    'error': 'conditional_failed',
                    'code': self.error_support.get_error_code('conditional_failed')
                })
        return {'valid': len(errors) == 0, 'errors': errors}
