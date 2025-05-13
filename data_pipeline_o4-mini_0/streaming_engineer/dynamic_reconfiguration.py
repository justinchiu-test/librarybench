class DynamicReconfiguration:
    def __init__(self, initial_config=None):
        self.config = initial_config or {}

    def update_config(self, new_config):
        self.config.update(new_config)

    def get(self, key, default=None):
        return self.config.get(key, default)
