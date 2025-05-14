import tomllib

def loads(s: str):
    return tomllib.loads(s)

def dumps(d: dict):
    """
    Minimal TOML serializer for dicts with list values.
    """
    lines = []
    for key, value in d.items():
        # Only support list of basic types (e.g. str, int)
        if isinstance(value, list):
            items = []
            for item in value:
                if isinstance(item, str):
                    items.append(f'"{item}"')
                else:
                    items.append(str(item))
            lines.append(f"{key} = [{', '.join(items)}]")
        else:
            # basic scalar
            val = f'"{value}"' if isinstance(value, str) else str(value)
            lines.append(f"{key} = {val}")
    return "\n".join(lines)
