import pickle

def packb(obj):
    """Stub packb: just pickle the object."""
    return pickle.dumps(obj)

def unpackb(data):
    """Stub unpackb: just unpickle the data."""
    return pickle.loads(data)
