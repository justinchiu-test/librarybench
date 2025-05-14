def validate_length(value, expected_length):
    if not hasattr(value, '__len__'):
        return False
    return len(value) == expected_length
