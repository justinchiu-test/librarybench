import re

def _parse_version(vstr):
    parts = vstr.split(".")
    nums = []
    for p in parts:
        if p.isdigit():
            nums.append(int(p))
        else:
            m = re.match(r"(\d+)", p)
            nums.append(int(m.group(1)) if m else 0)
    return tuple(nums)

def _compare_versions(v1, v2):
    t1, t2 = _parse_version(v1), _parse_version(v2)
    for a, b in zip(t1, t2):
        if a != b:
            return -1 if a < b else 1
    if len(t1) != len(t2):
        longer, rest = (t2, t1) if len(t1) < len(t2) else (t1, t2)
        if any(x > 0 for x in longer[len(rest):]):
            return -1 if len(t1) < len(t2) else 1
    return 0

_ops = {
    "==": lambda c: lambda v: _compare_versions(v, c) == 0,
    ">=": lambda c: lambda v: _compare_versions(v, c) >= 0,
    "<=": lambda c: lambda v: _compare_versions(v, c) <= 0,
    ">":  lambda c: lambda v: _compare_versions(v, c) > 0,
    "<":  lambda c: lambda v: _compare_versions(v, c) < 0,
}

def _parse_constraints(constraint_str):
    funcs = []
    for part in filter(None, (p.strip() for p in constraint_str.split(","))):
        for op in _ops:
            if part.startswith(op):
                funcs.append(_ops[op](part[len(op):].strip()))
                break
        else:
            raise ValueError(f"Invalid constraint: {part}")
    return funcs

class DependencySolver:
    def __init__(self, repo_manager):
        self.repo_manager = repo_manager

    def solve(self, constraints):
        available = self.repo_manager.get_all_packages()
        result = {}
        for pkg, cstr in constraints.items():
            vers = available.get(pkg)
            if not vers:
                raise KeyError(f"Package '{pkg}' not found in any repo")
            funcs = _parse_constraints(cstr)
            valid = [v for v in vers if all(f(v) for f in funcs)]
            if not valid:
                raise ValueError(f"No version for '{pkg}' satisfies '{cstr}'")
            valid.sort(key=_parse_version)
            result[pkg] = valid[-1]
        return result
