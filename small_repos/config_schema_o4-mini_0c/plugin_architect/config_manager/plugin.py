_plugin_hooks = {
    'loaders': [],
    'validators': [],
    'transformers': [],
    'postprocessors': [],
}

def register_plugin(**hooks):
    for hook, func in hooks.items():
        if hook not in _plugin_hooks:
            raise ValueError(f"Unknown hook '{hook}'")
        _plugin_hooks[hook].append(func)

def get_plugins(hook):
    return list(_plugin_hooks.get(hook, []))
