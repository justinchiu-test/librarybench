def no_pii(data):
    errors = []
    for field in ['ssn', 'email', 'name']:
        if isinstance(data, dict) and field in data:
            errors.append((field, "PII not allowed"))
    return errors
