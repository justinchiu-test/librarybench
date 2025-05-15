"""
Minimal YAML stub to satisfy safe_dump and safe_load in environments
where PyYAML is not installed. Uses JSON as a subset of YAML.
"""

import json

def safe_dump(data):
    """
    Serialize `data` to a YAML‐like string. Here we emit JSON,
    which is a valid subset of YAML.
    """
    return json.dumps(data)

def safe_load(s):
    """
    Parse a YAML‐like string. Here we assume JSON input.
    """
    return json.loads(s)
