import functools

def validate_params(schema):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for name, expected in schema.items():
                if name in kwargs:
                    val = kwargs[name]
                else:
                    continue
                if not isinstance(val, expected):
                    raise ValueError(f"Parameter {name} must be {expected.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
