"""
Hook registry for Security Analyst CLI.
"""
_before = []
_after = []

def register_hook(name, fn, when='pre'):
    if when == 'pre':
        _before.append(fn)
    elif when == 'post':
        _after.append(fn)
    else:
        raise ValueError(f"Invalid when: {when}")

def run_hooks(cmd, when='pre'):
    hooks = _before if when == 'pre' else _after if when == 'post' else []
    for fn in hooks:
        fn(cmd)