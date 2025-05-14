_startup_hooks = []
_pre_shutdown_hooks = []
_post_shutdown_hooks = []

def register_lifecycle_hook(event, func):
    if event == 'startup':
        _startup_hooks.append(func)
    elif event == 'pre_shutdown':
        _pre_shutdown_hooks.append(func)
    elif event == 'post_shutdown':
        _post_shutdown_hooks.append(func)
    else:
        raise ValueError('Unknown event')

def run_startup_hooks():
    for f in _startup_hooks:
        f()

def run_pre_shutdown_hooks():
    for f in _pre_shutdown_hooks:
        f()

def run_post_shutdown_hooks():
    for f in _post_shutdown_hooks:
        f()
