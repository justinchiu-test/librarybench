"""
Minimal toml stub for parsing and dumping top‐level tables.
Uses built-in tomllib for loading and a very simple dump implementation.
"""
import tomllib

def load(f):
    # delegate to tomllib
    return tomllib.load(f)

def dump(data, f):
    # Very basic dump: expects data to be dict of dicts
    for section, values in data.items():
        f.write(f'[{section}]\n')
        for k, v in values.items():
            if isinstance(v, str):
                f.write(f'{k} = "{v}"\n')
            else:
                f.write(f'{k} = {v}\n')
