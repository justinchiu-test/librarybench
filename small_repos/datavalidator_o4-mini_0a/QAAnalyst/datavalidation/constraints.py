class LengthConstraints:
    def __init__(self, limits):
        self.limits = limits

    def check_length(self, record):
        violations = []
        for field, max_len in self.limits.items():
            if field in record and isinstance(record[field], str) and len(record[field]) > max_len:
                violations.append({'field': field})
        return violations

class OptionalFields:
    def __init__(self, optional_fields, strict=True):
        self.optional_fields = optional_fields
        self.strict = strict

    def check_optional(self, record):
        violations = []
        if self.strict:
            for field in self.optional_fields:
                if field not in record or record[field] is None:
                    violations.append({'field': field})
        return violations
