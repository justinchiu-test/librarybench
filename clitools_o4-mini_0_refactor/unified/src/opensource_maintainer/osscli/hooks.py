"""
Hook management for open-source maintainers.
"""
_hooks = {'pre': {}, 'post': {}}

def register_hook(name, func, when='pre'):
    if when not in _hooks:
        raise ValueError(f"Invalid hook time: {when}")
    _hooks[when].setdefault(name, []).append(func)

def get_hooks(when):
    if when not in _hooks:
        raise ValueError(f"Invalid hook time: {when}")
    return _hooks[when]