import re

def safe_load(stream):
    """
    Minimal YAML loader that handles simple key: value mappings.
    """
    if hasattr(stream, 'read'):
        text = stream.read()
    else:
        text = stream
    data = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            key = k.strip()
            val = v.strip()
            # parse numeric
            if re.match(r'^[+-]?\d+$', val):
                parsed = int(val)
            elif re.match(r'^[+-]?\d*\.\d+', val):
                parsed = float(val)
            else:
                parsed = val
            data[key] = parsed
    return data
