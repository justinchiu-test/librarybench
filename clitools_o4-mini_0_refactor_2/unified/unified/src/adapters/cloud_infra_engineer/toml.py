"""
Simple TOML dump/load for Cloud Infrastructure Engineer CLI.
"""
def dumps(data):
    """Serialize dict `data` with sections as TOML."""
    out = ''
    for section, mapping in data.items():
        if isinstance(mapping, dict):
            out += f"[{section}]\n"
            for key, val in mapping.items():
                if isinstance(val, list):
                    items = ', '.join(f'"{item}"' if isinstance(item, str) else str(item) for item in val)
                    out += f"{key} = [{items}]\n"
                elif isinstance(val, str):
                    out += f"{key} = \"{val}\"\n"
                else:
                    out += f"{key} = {val}\n"
        else:
            if isinstance(mapping, str):
                out += f"{section} = \"{mapping}\"\n"
            else:
                out += f"{section} = {mapping}\n"
    return out

def loads(s):
    """Parse TOML string `s` into nested dict."""
    result = {}
    current = None
    for line in s.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            current = line[1:-1]
            result[current] = {}
        elif '=' in line and current is not None:
            key, val = line.split('=', 1)
            key = key.strip()
            v = val.strip()
            if v.startswith('[') and v.endswith(']'):
                inner = v[1:-1]
                items = [item.strip().strip('"').strip("'") for item in inner.split(',') if item.strip()]
                result[current][key] = items
            elif v.startswith('"') and v.endswith('"'):
                result[current][key] = v[1:-1]
            else:
                try:
                    result[current][key] = int(v)
                except ValueError:
                    try:
                        result[current][key] = float(v)
                    except ValueError:
                        result[current][key] = v
    return result