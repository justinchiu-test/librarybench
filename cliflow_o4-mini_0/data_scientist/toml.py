import re

def load(fp):
    """
    Stub TOML loader: handle lines of the form
      key = value
    where value is an unquoted number or a quoted string.
    """
    text = fp.read()
    result = {}
    for line in text.splitlines():
        line = line.strip()
        # skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        key, val = line.split('=', 1)
        key = key.strip()
        val = val.strip()
        # quoted string?
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            result[key] = val[1:-1]
        else:
            # try integer
            if re.match(r'^-?\d+$', val):
                result[key] = int(val)
            # try float
            elif re.match(r'^-?\d+\.\d*$', val):
                result[key] = float(val)
            else:
                # fallback to raw string
                result[key] = val
    return result
