from collections import defaultdict

class ConfigWatcher:
    def __init__(self):
        self.callbacks = defaultdict(list)

    def register(self, event, callback):
        self.callbacks[event].append(callback)

    def notify(self, event, **kwargs):
        for cb in self.callbacks.get(event, []):
            cb(**kwargs)

class HotReload:
    def __init__(self, paths, callback):
        self.paths = set(paths)
        self.callback = callback

    def simulate_change(self, path):
        if path in self.paths:
            self.callback(path)
