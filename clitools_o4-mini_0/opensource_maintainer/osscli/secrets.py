import os

def fetch_secret(backend="env", key=None, path=None):
    if backend == "env":
        return os.environ.get(key)
    elif backend == "file":
        if not path:
            raise ValueError("Path required for file backend")
        with open(path) as f:
            return f.read().strip()
    else:
        raise ValueError("Unknown backend")
