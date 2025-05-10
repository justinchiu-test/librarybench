import re

def dumps(data):
    """
    Minimal TOML serializer for nested dicts.
    """
    lines = []
    def recurse(cur, prefix=None):
        prefix = prefix or []
        # collect non-dict items
        simple = {k: v for k, v in cur.items() if not isinstance(v, dict)}
        if prefix and simple:
            lines.append(f"[{'.'.join(prefix)}]")
        for k, v in simple.items():
            if isinstance(v, str):
                val = f'"{v}"'
            elif isinstance(v, bool):
                val = "true" if v else "false"
            else:
                val = str(v)
            lines.append(f"{k} = {val}")
        # recurse into nested dicts
        for k, v in cur.items():
            if isinstance(v, dict):
                recurse(v, prefix + [k])

    recurse(data, [])
    return "\n".join(lines) + "\n"

def load(fpath_or_file):
    """
    Minimal TOML loader that handles tables and key/value pairs.
    """
    if hasattr(fpath_or_file, 'read'):
        content = fpath_or_file.read()
    else:
        with open(fpath_or_file, 'r') as f:
            content = f.read()
    data = {}
    current_section = []

    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            sect = line[1:-1].strip()
            current_section = sect.split('.')
            # ensure nested dict path exists
            d = data
            for part in current_section:
                if part not in d or not isinstance(d[part], dict):
                    d[part] = {}
                d = d[part]
        elif '=' in line:
            k, v = line.split('=', 1)
            key = k.strip()
            val = v.strip()
            # parse value
            if val.startswith('"') and val.endswith('"'):
                parsed = val[1:-1]
            elif re.match(r'^[+-]?\d+$', val):
                parsed = int(val)
            elif re.match(r'^[+-]?\d*\.\d+', val):
                parsed = float(val)
            elif val.lower() in ('true', 'false'):
                parsed = val.lower() == 'true'
            else:
                parsed = val
            # assign into data
            if current_section:
                d = data
                for part in current_section:
                    d = d[part]
                d[key] = parsed
            else:
                data[key] = parsed
    return data
