"""
Hook registration and execution for security analysts.
"""
_hooks = {'pre': [], 'post': []}

def register_hook(name, func, when='pre'):
    if when not in _hooks:
        raise ValueError(f"Invalid hook time: {when}")
    _hooks[when].append(func)

def run_hooks(cmd, when='pre'):
    for func in _hooks.get(when, []):
        func(cmd)