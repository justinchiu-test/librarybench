class HookManager:
    def __init__(self):
        self._pre_hooks = []
        self._post_hooks = []

    def add_pre_hook(self, func):
        self._pre_hooks.append(func)

    def add_post_hook(self, func):
        self._post_hooks.append(func)

    def run_pre(self, *args, **kwargs):
        for hook in self._pre_hooks:
            hook(*args, **kwargs)

    def run_post(self, *args, **kwargs):
        for hook in self._post_hooks:
            hook(*args, **kwargs)
