"""
A minimal TOML stub to satisfy tests that import toml.
Provides simple dumps and loads for flat dictionaries.
"""
def dumps(data):
    if not isinstance(data, dict):
        raise TypeError("toml.dumps() supports only dicts")
    lines = []
    for key, value in data.items():
        if isinstance(value, str):
            val = f'"{value}"'
        elif isinstance(value, bool):
            val = 'true' if value else 'false'
        elif value is None:
            val = '""'
        else:
            val = str(value)
        lines.append(f"{key} = {val}")
    # Add trailing newline for neatness
    return "\n".join(lines) + "\n"

def loads(s):
    result = {}
    for raw in s.splitlines():
        line = raw.strip()
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        key, val = line.split('=', 1)
        key = key.strip()
        val = val.strip()
        # String literal
        if val.startswith('"') and val.endswith('"'):
            result[key] = val[1:-1]
        # Boolean
        elif val.lower() in ('true', 'false'):
            result[key] = val.lower() == 'true'
        else:
            # Try integer
            try:
                result[key] = int(val)
            except ValueError:
                # Try float
                try:
                    result[key] = float(val)
                except ValueError:
                    # Fallback to raw string
                    result[key] = val
    return result
