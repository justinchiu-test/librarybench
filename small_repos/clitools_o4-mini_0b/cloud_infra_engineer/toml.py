"""
Minimal TOML support for load, loads, dump, dumps.
Uses built-in tomllib for parsing (Python 3.11+).
"""
import tomllib

def loads(s: str):
    return tomllib.loads(s)

def load(fp):
    return tomllib.load(fp)

def dumps(obj) -> str:
    lines = []
    def format_val(v):
        if isinstance(v, str):
            return '"' + v.replace('"', '\\"') + '"'
        if isinstance(v, bool):
            return 'true' if v else 'false'
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, list):
            items = ', '.join(format_val(i) for i in v)
            return f"[{items}]"
        if v is None:
            return '""'
        raise TypeError(f"Unsupported type: {type(v)}")

    def serialize(table, prefix=None):
        # simple keys
        for key, value in table.items():
            if not isinstance(value, dict):
                lines.append(f"{key} = {format_val(value)}")
        # nested tables
        for key, value in table.items():
            if isinstance(value, dict):
                header = f"[{key}]" if prefix is None else f"[{prefix}.{key}]"
                lines.append("")  # blank line before a new table
                lines.append(header)
                serialize(value, key if prefix is None else f"{prefix}.{key}")

    serialize(obj)
    return "\n".join(lines).lstrip() + "\n"

def dump(obj, fp):
    fp.write(dumps(obj))
