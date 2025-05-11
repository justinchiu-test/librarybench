# coding: utf-8
"""
Simple YAML dump/load wrapper
"""
try:
    import yaml as _yaml
    dump = _yaml.dump
    safe_load = _yaml.safe_load
except ImportError:
    # Fallback to JSON representation for simplicity
    import json as _json
    def dump(data):
        return _json.dumps(data)
    def safe_load(data):
        return _json.loads(data)