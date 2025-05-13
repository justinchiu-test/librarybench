"""
Hook registry for DevOps Engineer CLI.
"""
class HookRegistry:
    def __init__(self):
        self.pre_hooks = []
        self.post_hooks = []

    def register_pre(self, fn):
        self.pre_hooks.append(fn)

    def register_post(self, fn):
        self.post_hooks.append(fn)

    def execute_pre(self, *args, **kwargs):
        for fn in self.pre_hooks:
            fn(*args, **kwargs)

    def execute_post(self, *args, **kwargs):
        for fn in self.post_hooks:
            fn(*args, **kwargs)