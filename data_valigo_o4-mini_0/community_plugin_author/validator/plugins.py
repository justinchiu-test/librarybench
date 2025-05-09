_rules = {}
_transformers = {}

def register_rule(name: str, profile: str = None):
    def decorator(fn):
        _rules.setdefault(name, []).append((fn, profile))
        return fn
    return decorator

def get_rule(name: str, profile: str = None):
    candidates = _rules.get(name, [])
    for fn, prof in candidates:
        if prof == profile:
            return fn
    for fn, prof in candidates:
        if prof is None:
            return fn
    return None

def register_transformer(name: str):
    def decorator(fn):
        _transformers[name] = fn
        return fn
    return decorator

def get_transformer(name: str):
    return _transformers.get(name)
