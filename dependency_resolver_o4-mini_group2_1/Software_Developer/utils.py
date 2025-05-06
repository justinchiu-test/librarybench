import os
import json
import re

def load_json(path):
    """Load JSON data from a file."""
    with open(path) as f:
        return json.load(f)

def save_json(path, data, indent=2):
    """Save data as JSON to a file, creating parent directories if needed."""
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)

def ensure_dir(path):
    """Ensure that a directory exists."""
    if not os.path.isdir(path):
        os.makedirs(path)

def json_file_path(base_dir, name):
    """Construct a .json filename under base_dir from a name (no extension)."""
    return os.path.join(base_dir, f"{name}.json")

def parse_version(vstr):
    """Parse a version string into a tuple of ints, dropping non-numeric suffixes."""
    parts = []
    for p in vstr.split("."):
        if p.isdigit():
            parts.append(int(p))
        else:
            m = re.match(r"(\d+)", p)
            parts.append(int(m.group(1)) if m else 0)
    return tuple(parts)

def compare_versions(a, b):
    """Compare two version strings. Return -1, 0, 1 for a<b, a==b, a>b."""
    t1, t2 = parse_version(a), parse_version(b)
    for x, y in zip(t1, t2):
        if x < y: return -1
        if x > y: return 1
    # if one is longer
    if len(t1) < len(t2):
        if any(v>0 for v in t2[len(t1):]): return -1
    elif len(t1) > len(t2):
        if any(v>0 for v in t1[len(t2):]): return 1
    return 0

_ops = {
    "==": lambda c: lambda v: compare_versions(v, c)==0,
    ">=": lambda c: lambda v: compare_versions(v, c)>=0,
    "<=": lambda c: lambda v: compare_versions(v, c)<=0,
    ">":  lambda c: lambda v: compare_versions(v, c)>0,
    "<":  lambda c: lambda v: compare_versions(v, c)<0,
}

def parse_constraints(cstr):
    """
    Parse a constraint string like ">=1.0, <2.0" into a list of callables
    that accept a version string and return True/False.
    """
    parts = [p.strip() for p in cstr.split(",") if p.strip()]
    funcs = []
    for part in parts:
        for op, ctor in _ops.items():
            if part.startswith(op):
                ver = part[len(op):].strip()
                funcs.append(ctor(ver))
                break
        else:
            raise ValueError(f"Invalid constraint: {part}")
    return funcs

def match_constraint(version, constraint):
    """
    Check if a version string satisfies a constraint like ">=1.0.0,<2.0.0".
    Supports ==, >=, <=, >, <.
    """
    conds = [c.strip() for c in constraint.split(",") if c.strip()]
    for cond in conds:
        m = re.match(r"(>=|<=|==|>|<)(\d+(?:\.\d+)*)$", cond)
        if not m:
            raise ValueError(f"Invalid constraint: {cond}")
        op, ver = m.groups()
        cmp = compare_versions(version, ver)
        if op == "==" and cmp != 0: return False
        if op == ">"  and cmp != 1: return False
        if op == "<"  and cmp != -1: return False
        if op == ">=" and cmp not in (0,1): return False
        if op == "<=" and cmp not in (0,-1): return False
    return True
