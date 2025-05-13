# A minimal YAML stub so tests that do "import yaml" and
# pipeline.py’s YAML bits work without requiring PyYAML.
import json

def safe_dump(data, stream=None):
    """
    If a stream is given, write JSON into it.
    Otherwise return a JSON string (as YAML stand‐in).
    """
    if stream is not None:
        json.dump(data, stream)
    else:
        return json.dumps(data)

def safe_load(stream):
    """
    If a string is passed, parse JSON from it.
    Otherwise treat stream as file‐like and json.load.
    """
    if isinstance(stream, str):
        return json.loads(stream)
    else:
        return json.load(stream)
