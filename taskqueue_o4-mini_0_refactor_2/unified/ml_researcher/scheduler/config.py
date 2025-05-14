class ConfigManager:
    def __init__(self, initial_config=None):
        self.config = initial_config or {}
        self.subscribers = []
    def get(self, key, default=None):
        return self.config.get(key, default)
    def update(self, new_config):
        self.config.update(new_config)
        for callback in self.subscribers:
            callback(self.config)
    def subscribe(self, callback):
        self.subscribers.append(callback)
