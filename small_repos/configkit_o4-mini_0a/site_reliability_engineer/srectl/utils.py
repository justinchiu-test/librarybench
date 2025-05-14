import re

def nested_merge(a, b):
    """
    Merge nested dict b into a, replacing lists entirely.
    """
    result = dict(a)
    for key, b_val in b.items():
        if key in result:
            a_val = result[key]
            if isinstance(a_val, dict) and isinstance(b_val, dict):
                result[key] = nested_merge(a_val, b_val)
            elif isinstance(b_val, list):
                result[key] = b_val
            else:
                result[key] = b_val
        else:
            result[key] = b_val
    return result

def custom_coerce(value):
    """
    Coerce percentages, rates, and time units into numeric types.
    """
    if isinstance(value, (int, float)):
        return value
    if not isinstance(value, str):
        return value
    s = value.strip()
    # Percentage
    if s.endswith('%'):
        try:
            num = float(s[:-1])
            return num / 100.0
        except ValueError:
            pass
    # Milliseconds
    if s.endswith('ms'):
        try:
            num = float(s[:-2])
            return num / 1000.0
        except ValueError:
            pass
    # Seconds
    if s.endswith('s') and not s.endswith('ms'):
        try:
            num = float(s[:-1])
            return num
        except ValueError:
            pass
    # Minutes
    if s.endswith('m') and not s.endswith('ms'):
        try:
            num = float(s[:-1])
            return num * 60.0
        except ValueError:
            pass
    # Rates e.g. 100r/s
    m = re.match(r'^(\d+(\.\d+)?)[rR]/s$', s)
    if m:
        return float(m.group(1))
    # Plain number
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        pass
    return value
