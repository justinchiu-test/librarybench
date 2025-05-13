import pickle

def packb(obj, use_bin_type=False):
    """
    Serialize `obj` to bytes. The `use_bin_type` parameter is accepted
    for compatibility with the API but ignored here.
    """
    return pickle.dumps(obj)

def unpackb(data, raw=False):
    """
    Deserialize bytes back to Python object. The `raw` parameter is accepted
    for compatibility but ignored here.
    """
    return pickle.loads(data)
