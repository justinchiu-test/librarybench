import re

def parse_version(v):
    # Split by dots, convert numeric segments to ints
    parts = []
    for seg in v.split('.'):
        if seg.isdigit():
            parts.append(int(seg))
        else:
            # fallback: strip non-digits
            m = re.match(r'(\d+)', seg)
            parts.append(int(m.group(1)) if m else seg)
    return parts

def compare_versions(a, b):
    pa = parse_version(a)
    pb = parse_version(b)
    for x, y in zip(pa, pb):
        if x < y: return -1
        if x > y: return 1
    # ties so far
    if len(pa) < len(pb): return -1
    if len(pa) > len(pb): return 1
    return 0
