_strategies = {}

def register_strategy(name, func):
    _strategies[name] = func

def get_strategy(name):
    return _strategies.get(name)

def append_strategy(existing, new):
    if existing is None:
        return list(new)
    return existing + list(new)

def replace_strategy(existing, new):
    return list(new)

# register defaults
register_strategy("append", append_strategy)
register_strategy("replace", replace_strategy)
