"""
Hook registry for devops engineers.
"""
class HookRegistry:
    def __init__(self):
        self._pre_hooks = []
        self._post_hooks = []

    def register_pre(self, func):
        self._pre_hooks.append(func)

    def register_post(self, func):
        self._post_hooks.append(func)

    def execute_pre(self, *args, **kwargs):
        for func in self._pre_hooks:
            func(*args, **kwargs)

    def execute_post(self, *args, **kwargs):
        for func in self._post_hooks:
            func(*args, **kwargs)