class DefaultFallback:
    def __init__(self, defaults):
        self.defaults = defaults or {}

    def get(self, key, default=None):
        return self.defaults.get(key, default)
