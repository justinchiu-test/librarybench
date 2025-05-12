import collections.abc

class DefaultFallback:
    @staticmethod
    def get_defaults():
        return {
            'physics': {
                'gravity': 9.8,
                'friction': 0.5
            },
            'spawn': {
                'rate': 1.0
            },
            'ui': {
                'scale': 1.0
            }
        }

def nested_merge(a, b):
    """
    Merge dict b into dict a: nested dicts are merged, lists in b override a.
    """
    result = dict(a)
    for key, value in b.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = nested_merge(result[key], value)
        else:
            result[key] = value
    return result
