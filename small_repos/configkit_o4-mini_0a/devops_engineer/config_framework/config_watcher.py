class ConfigWatcher:
    def __init__(self, initial_config=None):
        self.config = initial_config or {}
        self.handlers = {}

    def register(self, key, handler):
        self.handlers.setdefault(key, []).append(handler)

    def update(self, new_config):
        for key, handlers in self.handlers.items():
            old = self.config.get(key)
            new = new_config.get(key)
            if new != old:
                for h in handlers:
                    h(key, old, new)
        self.config = new_config
