"""
HookManager: manage registration and emission of events
"""
class HookManager:
    def __init__(self):
        self._hooks = {}
    def register(self, event, func):
        self._hooks.setdefault(event, []).append(func)
    def emit(self, event, *args, **kwargs):
        for func in self._hooks.get(event, []):
            try:
                func(*args, **kwargs)
            except Exception:
                pass