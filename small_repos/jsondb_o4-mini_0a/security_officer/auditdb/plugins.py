class PluginManager:
    def __init__(self):
        self.hooks = {
            "pre_upsert": [],
            "post_upsert": [],
            "pre_delete": [],
            "post_delete": [],
            "pre_soft_delete": [],
            "post_soft_delete": []
        }

    def register(self, hook_name: str, fn):
        if hook_name not in self.hooks:
            raise KeyError(f"Invalid hook: {hook_name}")
        self.hooks[hook_name].append(fn)

    def run(self, hook_name: str, *args, **kwargs):
        for fn in self.hooks.get(hook_name, []):
            fn(*args, **kwargs)
