import os
_loaders = {}

def register_loader(extension, func):
    _loaders[extension] = func

def load_config(path):
    ext = os.path.splitext(path)[1]
    loader = _loaders.get(ext)
    if not loader:
        raise ValueError(f"No loader for extension {ext}")
    return loader(path)
