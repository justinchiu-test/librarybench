class ProfileManager:
    def __init__(self, base_config):
        self.base = base_config
        self.profiles = {}

    def add_profile(self, name, config):
        self.profiles[name] = config

    def load(self, name):
        cfg = self.base
        if name in self.profiles:
            cfg = Config().merge(self.base).merge(self.profiles[name])
        return cfg
from .config import Config
