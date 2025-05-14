import collections.abc

def nested_merge(base, override):
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = nested_merge(result[k], v)
        elif k == 'callbacks' and isinstance(v, list):
            result[k] = v
        else:
            result[k] = v
    return result
