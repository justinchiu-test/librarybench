class ConditionalValidation:
    def apply_conditional(self, data, rules):
        errors = []
        for condition, then_field, code in rules or []:
            if condition(data) and then_field not in data:
                errors.append({
                    'field': then_field,
                    'error': 'conditional',
                    'code': code
                })
        return errors
