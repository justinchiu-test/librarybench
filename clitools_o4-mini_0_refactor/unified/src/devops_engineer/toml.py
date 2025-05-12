"""
TOML support for devops_engineer.
"""
"""
Minimal TOML parser and dumper for devops_engineer.
Supports simple tables and key-values.
"""
import os

def dump(data, file_obj):
    # data: dict of {section: {key: value}}
    for section, values in data.items():
        file_obj.write(f"[{section}]\n")
        for k, v in values.items():
            if isinstance(v, str):
                file_obj.write(f"{k} = \"{v}\"\n")
            elif isinstance(v, bool):
                file_obj.write(f"{k} = {str(v).lower()}\n")
            else:
                file_obj.write(f"{k} = {v}\n")

def load(path):
    result = {}
    section = None
    if not os.path.exists(path):
        return result
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]
                result[section] = {}
            elif '=' in line and section:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip()
                # parse basic types
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                elif val.lower() in ('true', 'false'):
                    val = val.lower() == 'true'
                else:
                    try:
                        if '.' in val:
                            val = float(val)
                        else:
                            val = int(val)
                    except ValueError:
                        pass
                result[section][key] = val
    return result