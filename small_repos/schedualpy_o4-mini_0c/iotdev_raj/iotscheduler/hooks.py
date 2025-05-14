class HookManager:
    def __init__(self):
        self._pre_hooks = []
        self._post_hooks = []

    def register(self, pre_hook=None, post_hook=None):
        """
        Register a pre- or post- hook. Both are optional; you can register
        multiple hooks in multiple calls.
        """
        if pre_hook is not None:
            self._pre_hooks.append(pre_hook)
        if post_hook is not None:
            self._post_hooks.append(post_hook)

    def run_pre(self, task_id, info):
        """
        Run all registered pre-hooks in the order they were added.
        """
        for hook in self._pre_hooks:
            hook(task_id, info)

    def run_post(self, task_id, info):
        """
        Run all registered post-hooks in the order they were added.
        """
        for hook in self._post_hooks:
            hook(task_id, info)
