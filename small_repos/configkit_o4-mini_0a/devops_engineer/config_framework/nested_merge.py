def nested_merge(a, b):
    result = {}
    for key in set(a) | set(b):
        if key in a and key in b:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                result[key] = nested_merge(a[key], b[key])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                result[key] = b[key]
            else:
                result[key] = b[key]
        elif key in b:
            result[key] = b[key]
        else:
            result[key] = a[key]
    return result
