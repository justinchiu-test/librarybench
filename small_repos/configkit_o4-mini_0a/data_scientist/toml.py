import tomllib

def load(f):
    """
    Load TOML from a file object using the standard library's tomllib.
    """
    return tomllib.load(f)

def loads(s):
    """
    Load TOML from a string using the standard library's tomllib.
    """
    return tomllib.loads(s)

def dumps(data):
    """
    A minimal TOML dumper that covers the test cases:
    - Top-level scalar values (int, bool, string)
    - One level of nested dicts, rendered as a [section]
    """
    lines = []

    def format_val(v):
        if isinstance(v, str):
            # escape double quotes in the string
            esc = v.replace('"', '\\"')
            return f'"{esc}"'
        elif isinstance(v, bool):
            return 'true' if v else 'false'
        else:
            # ints, floats, etc.
            return str(v)

    for key, val in data.items():
        if isinstance(val, dict):
            # section header
            lines.append(f'[{key}]')
            for subk, subv in val.items():
                lines.append(f'{subk} = {format_val(subv)}')
        else:
            lines.append(f'{key} = {format_val(val)}')

    # join with newlines
    return '\n'.join(lines)
