import os

class EnvLoader:
    def __init__(self, prefix='CLUSTER_'):
        self.prefix = prefix

    def load(self):
        config = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix):].lower()
                config[config_key] = value
        return config
