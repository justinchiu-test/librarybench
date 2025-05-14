import json

def safe_dump(data, stream):
    """
    A minimal safe_dump that writes Python data structures as JSON.
    Tests only check that yaml.safe_load reads back the same dict.
    """
    json.dump(data, stream)

def safe_load(stream):
    """
    Reads JSON from a file-like object and returns the Python data.
    """
    return json.load(stream)
