try:
    import tomllib
except ImportError:
    import toml as tomllib

class TOMLLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        with open(self.path, 'rb') as f:
            return tomllib.load(f)
