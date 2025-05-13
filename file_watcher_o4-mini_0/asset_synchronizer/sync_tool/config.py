import json
import os

class Config:
    def __init__(self, path):
        self.path = path
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Config file {self.path} not found")
        if self.path.endswith('.json'):
            with open(self.path, 'r') as f:
                return json.load(f)
        elif self.path.endswith('.toml'):
            try:
                import toml  # defer import until needed
            except ImportError:
                raise ImportError("toml library is required to load TOML config")
            with open(self.path, 'r') as f:
                return toml.load(f)
        else:
            raise ValueError("Unsupported config file format")

    def get(self, key, default=None):
        return self.data.get(key, default)
