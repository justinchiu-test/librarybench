_hooks = {"pre": {}, "post": {}}

def register_hook(name, func, when="pre"):
    if when not in _hooks:
        raise ValueError("when must be 'pre' or 'post'")
    _hooks[when].setdefault(name, []).append(func)

def run_hooks(command, when="pre"):
    for funcs in _hooks.get(when, {}).values():
        for func in funcs:
            func(command)
