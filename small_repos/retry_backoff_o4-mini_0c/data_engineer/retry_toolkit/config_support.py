import os

def _load_simple_toml(path):
    data = {}
    current = None
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                current = line[1:-1]
                data[current] = {}
            elif '=' in line and current:
                k, v = map(str.strip, line.split('=', 1))
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                else:
                    if v.isdigit():
                        v = int(v)
                    else:
                        try:
                            v = float(v)
                        except:
                            pass
                data[current][k] = v
    return data

class ConfigFileSupport:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"No such config: {path}")
        self.config = _load_simple_toml(path)

    def get_retry_setting(self, key, default=None):
        return self.config.get('retry', {}).get(key, default)

    def get_backoff_setting(self, key, default=None):
        return self.config.get('backoff', {}).get(key, default)
