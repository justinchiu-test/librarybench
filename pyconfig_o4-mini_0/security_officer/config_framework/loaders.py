LOADER_REGISTRY = {}

def register_loader(name, func):
    LOADER_REGISTRY[name] = func

def load(name, data):
    if name not in LOADER_REGISTRY:
        raise KeyError(f"No loader registered for {name}")
    return LOADER_REGISTRY[name](data)
