_hooks = {"pre": {}, "post": {}}

def register_hook(name, func, when="pre"):
    if when not in _hooks:
        raise ValueError("Invalid hook time")
    _hooks[when].setdefault(name, []).append(func)

def get_hooks(when):
    return _hooks.get(when, {})
