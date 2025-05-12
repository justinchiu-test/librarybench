"""
Minimal YAML parser for security analysts.
"""
def safe_load(file_obj):
    data = {}
    for line in file_obj:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            # parse number if possible
            if val.isdigit():
                data[key] = int(val)
            else:
                try:
                    data[key] = float(val)
                except ValueError:
                    data[key] = val
    return data