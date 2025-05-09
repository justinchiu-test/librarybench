import re

def parse_version(v):
    parts = v.split(".")
    parts = [int(p) for p in parts]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

def compare_versions(a, b):
    a_parts = parse_version(a)
    b_parts = parse_version(b)
    if a_parts < b_parts:
        return -1
    elif a_parts > b_parts:
        return 1
    return 0

def match_constraint(version, constraint):
    """
    Check if a version string satisfies a constraint like ">=1.0.0,<2.0.0".
    Supported operators: ==, >=, <=, >, <
    """
    conds = [c.strip() for c in constraint.split(",") if c.strip()]
    for cond in conds:
        m = re.match(r"(>=|<=|==|>|<)(\d+\.\d+(?:\.\d+)*)$", cond)
        if not m:
            raise ValueError(f"Invalid constraint: {cond}")
        op, ver = m.group(1), m.group(2)
        cmp = compare_versions(version, ver)
        if op == "==":
            if cmp != 0:
                return False
        elif op == ">":
            if cmp != 1:
                return False
        elif op == "<":
            if cmp != -1:
                return False
        elif op == ">=":
            if cmp not in (0, 1):
                return False
        elif op == "<=":
            if cmp not in (0, -1):
                return False
    return True
