# Shared utility functions for all modules

import os
import json

def parse_version(v: str):
    """Convert a version string into a tuple of ints."""
    return tuple(int(x) for x in v.split("."))

def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two semantic version strings.
    Returns -1 if v1<v2, 0 if equal, +1 if v1>v2.
    """
    p1 = parse_version(v1)
    p2 = parse_version(v2)
    length = max(len(p1), len(p2))
    p1 += (0,) * (length - len(p1))
    p2 += (0,) * (length - len(p2))
    if p1 < p2: return -1
    if p1 > p2: return 1
    return 0

def parse_constraints(spec: str):
    """
    Parse a spec like "name>=1.0,<2.0" or "==1.0" or "name".
    Returns (name:str, constraints:List[(op,version)]).
    """
    name = spec
    constraints = []
    for i, ch in enumerate(spec):
        if ch in "<>=":
            name = spec[:i]
            raw = spec[i:]
            for part in raw.split(","):
                part = part.strip()
                for op in ("==", ">=", "<=", ">", "<"):
                    if part.startswith(op):
                        constraints.append((op, part[len(op):]))
                        break
                else:
                    raise ValueError(f"Invalid constraint '{part}'")
            break
    return name, constraints

def satisfies_constraints(version: str, constraints) -> bool:
    """
    Check if a version string satisfies a list of (op,version) constraints.
    """
    for op, ver in constraints:
        cmp = compare_versions(version, ver)
        if op == "==" and cmp != 0: return False
        if op == ">=" and cmp < 0: return False
        if op == "<=" and cmp > 0: return False
        if op == ">"  and cmp <= 0: return False
        if op == "<"  and cmp >= 0: return False
    return True

def load_json(path: str):
    """Load JSON from a file, error if not exists."""
    if not os.path.exists(path):
        raise ValueError(f"File {path} not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data):
    """Save data as JSON, creating parent dirs if needed."""
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def read_lines(path: str):
    """Read all lines from a file, strip \\n, error if not exists."""
    if not os.path.exists(path):
        raise ValueError(f"File {path} not found")
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]

def write_lines(path: str, lines):
    """Write a list of lines into a file."""
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
