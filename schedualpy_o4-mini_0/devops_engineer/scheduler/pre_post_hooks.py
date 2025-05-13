class PrePostHooks:
    def __init__(self):
        self._pre_hooks = []
        self._post_hooks = []

    def register_pre_hook(self, func):
        if callable(func):
            self._pre_hooks.append(func)
        else:
            raise ValueError("Pre-hook must be callable")

    def register_post_hook(self, func):
        if callable(func):
            self._post_hooks.append(func)
        else:
            raise ValueError("Post-hook must be callable")

    def run_pre_hooks(self, *args, **kwargs):
        results = []
        for hook in self._pre_hooks:
            results.append(hook(*args, **kwargs))
        return results

    def run_post_hooks(self, *args, **kwargs):
        results = []
        for hook in self._post_hooks:
            results.append(hook(*args, **kwargs))
        return results
