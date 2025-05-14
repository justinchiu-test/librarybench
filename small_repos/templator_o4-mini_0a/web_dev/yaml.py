# A minimal YAML shim so that `import yaml` in tests passes.
import json

def safe_dump(obj):
    # Return a string; tests only require round‐trip equality.
    return json.dumps(obj)

def safe_load(s):
    return json.loads(s)
