"""
YAML parsing wrapper for DevOps Engineer CLI.
"""
"""
Simple YAML-like parser/writer supporting one level of nested dicts.
"""
import io

def safe_dump(data, stream):
    """Serialize `data` (dict) as simple YAML to `stream`."""
    for key, mapping in data.items():
        stream.write(f"{key}:\n")
        if isinstance(mapping, dict):
            for k, v in mapping.items():
                stream.write(f"  {k}: {v}\n")
        else:
            stream.write(f"  {mapping}\n")

def safe_load(stream):
    """Parse simple YAML from `stream` into a dict."""
    if isinstance(stream, io.IOBase):
        lines = stream.read().splitlines()
    else:
        lines = str(stream).splitlines()
    result = {}
    current = None
    for line in lines:
        if not line.strip():
            continue
        if not line.startswith(' '):
            # section
            if line.endswith(':'):
                current = line[:-1]
                result[current] = {}
            else:
                # key: value at root
                parts = line.split(':', 1)
                k = parts[0].strip()
                v = parts[1].strip() if len(parts)>1 else ''
                result[k] = int(v) if v.isdigit() else v
        else:
            # nested key
            parts = line.strip().split(':', 1)
            k = parts[0].strip()
            v = parts[1].strip() if len(parts)>1 else ''
            val = int(v) if v.isdigit() else v
            if current is not None:
                result[current][k] = val
    return result