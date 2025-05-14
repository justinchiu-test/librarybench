class ArgvLoader:
    def __init__(self, argv):
        self.argv = argv or []

    def load(self):
        config = {}
        for arg in self.argv:
            if arg.startswith('--'):
                arg = arg[2:]
            if '=' in arg:
                key, value = arg.split('=', 1)
                config[key] = value
        return config
