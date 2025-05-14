import os

class EnvVarOverrides:
    def __init__(self, prefix='RETRY'):
        self.prefix = prefix.upper()

    def get_max_attempts(self, default):
        val = os.getenv(f"{self.prefix}_MAX_ATTEMPTS")
        if val is not None:
            try:
                return int(val)
            except ValueError:
                return default
        return default

    def get_base(self, default):
        val = os.getenv(f"{self.prefix}_BASE")
        if val is not None:
            try:
                return float(val)
            except ValueError:
                return default
        return default

    def get_cap(self, default):
        val = os.getenv(f"{self.prefix}_CAP")
        if val is not None:
            try:
                return float(val)
            except ValueError:
                return default
        return default
