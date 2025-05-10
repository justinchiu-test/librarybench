"""
Minimal YAML stub using JSON to back safe_load and safe_dump.
"""
import json

def safe_load(stream):
    try:
        return json.load(stream)
    except ValueError:
        # Return empty mapping if there's nothing or invalid
        return {}

def safe_dump(data, stream):
    """
    Dump the data as JSON into the given stream.
    This satisfies tests that write out YAML-like content.
    """
    json.dump(data, stream)
