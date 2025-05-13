"""
TOML parsing wrapper for DevOps Engineer CLI.
"""
"""
Simple TOML-like parser/writer supporting one section of key-value pairs.
"""
import io

def dump(data, stream):
    """Serialize `data` (dict) as simple TOML to `stream`."""
    for section, mapping in data.items():
        stream.write(f"[{section}]\n")
        if isinstance(mapping, dict):
            for k, v in mapping.items():
                if isinstance(v, str):
                    stream.write(f'{k} = "{v}"\n')
                else:
                    stream.write(f"{k} = {v}\n")
        else:
            # flat key
            stream.write(f"{section} = {mapping}\n")

def load(stream):
    """Parse simple TOML from `stream` into a dict."""
    if isinstance(stream, io.IOBase):
        lines = stream.read().splitlines()
    else:
        lines = str(stream).splitlines()
    result = {}
    current = None
    for line in lines:
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
            if v.startswith('"') and v.endswith('"'):
                v_parsed = v[1:-1]
            else:
                try:
                    v_parsed = int(v)
                except ValueError:
                    try:
                        v_parsed = float(v)
                    except ValueError:
                        v_parsed = v
            result[current][key] = v_parsed
    return result