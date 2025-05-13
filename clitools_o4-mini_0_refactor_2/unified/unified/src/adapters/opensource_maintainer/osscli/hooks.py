"""
Hook registration for Open Source Maintainer CLI.
"""
_pre_hooks = {}
_post_hooks = {}

def register_hook(name, fn, when='pre'):
    if when == 'pre':
        _pre_hooks.setdefault(name, []).append(fn)
    elif when == 'post':
        _post_hooks.setdefault(name, []).append(fn)
    else:
        raise ValueError(f"Invalid when: {when}")

def get_hooks(when):
    if when == 'pre':
        return _pre_hooks
    elif when == 'post':
        return _post_hooks
    else:
        raise ValueError(f"Invalid when: {when}")