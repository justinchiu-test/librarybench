class ConfigWatcher:
    def __init__(self):
        self._callbacks = {}

    def register(self, key, callback):
        self._callbacks.setdefault(key, []).append(callback)

    def update(self, key, value):
        for cb in self._callbacks.get(key, []):
            cb(value)

class HotReload:
    def __init__(self):
        self._watches = {}

    def watch(self, path, callback):
        self._watches.setdefault(path, []).append(callback)

    def simulate_change(self, path):
        for cb in self._watches.get(path, []):
            cb(path)
