import re

_units = {
    'b': 1,
    'k': 1024,
    'kb': 1024,
    'm': 1024**2,
    'mb': 1024**2,
    'g': 1024**3,
    'gb': 1024**3,
    't': 1024**4,
    'tb': 1024**4,
}

def parse_bytes(s):
    if not isinstance(s, str):
        raise ValueError("Input must be a string")
    s = s.strip()
    match = re.fullmatch(r'(\d+(?:\.\d+)?)([a-zA-Z]+)?', s)
    if not match:
        raise ValueError(f"Invalid size: {s}")
    num, unit = match.groups()
    num = float(num)
    if unit:
        u = unit.lower()
        if u not in _units:
            raise ValueError(f"Unknown unit: {unit}")
        num *= _units[u]
    return int(num)
