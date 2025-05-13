_hooks = {
    'startup': [],
    'pre_shutdown': [],
    'post_shutdown': []
}

def register_lifecycle_hook(event, func):
    if event not in _hooks:
        raise ValueError("Unknown event")
    _hooks[event].append(func)

def trigger_lifecycle(event):
    if event not in _hooks:
        raise ValueError("Unknown event")
    for func in _hooks[event]:
        func()
