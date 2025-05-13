_hooks = {}

def register_hook(event, func):
    _hooks.setdefault(event, []).append(func)

def trigger_hook(event, *args, **kwargs):
    for func in _hooks.get(event, []):
        func(*args, **kwargs)
