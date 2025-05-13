"""
Stub YAML module using JSON parsing to satisfy dependencies.
Provides safe_load and dump functionality using the standard json module.
"""
import json

def safe_load(stream_or_str):
    """
    Load YAML content from a string or file-like object.
    Internally uses JSON parsing.
    """
    if isinstance(stream_or_str, str):
        return json.loads(stream_or_str)
    else:
        # assume file-like
        return json.load(stream_or_str)

def dump(data, stream=None):
    """
    Dump data to a YAML representation.
    If `stream` is None, returns a string; otherwise writes JSON to the stream.
    """
    if stream is None:
        return json.dumps(data)
    else:
        return json.dump(data, stream)
