class Context:
    def __init__(self):
        self.data = {}
        self.dry_run = False
        self.hooks = {
            'pre-command': [],
            'post-command': [],
            'on-error': [],
            'on-exit': [],
        }
    def register_hook(self, event, func):
        if event not in self.hooks:
            raise ValueError(f"Unknown event {event}")
        self.hooks[event].append(func)
    def run_hooks(self, event, *args, **kwargs):
        for func in self.hooks.get(event, []):
            func(*args, **kwargs)
