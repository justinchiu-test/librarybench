import re

def _parse_version(vstr):
    # split by dots, map to ints if possible
    parts = vstr.split(".")
    nums = []
    for p in parts:
        if p.isdigit():
            nums.append(int(p))
        else:
            # drop non-numeric suffix
            m = re.match(r"(\d+)", p)
            if m:
                nums.append(int(m.group(1)))
            else:
                nums.append(0)
    return tuple(nums)

def _compare_versions(v1, v2):
    t1 = _parse_version(v1)
    t2 = _parse_version(v2)
    # compare elementwise
    for a,b in zip(t1, t2):
        if a < b: return -1
        if a > b: return 1
    if len(t1) < len(t2):
        if any(x>0 for x in t2[len(t1):]): return -1
    elif len(t1) > len(t2):
        if any(x>0 for x in t1[len(t2):]): return 1
    return 0

_ops = {
    "==": lambda c: lambda v: _compare_versions(v, c)==0,
    ">=": lambda c: lambda v: _compare_versions(v, c)>=0,
    "<=": lambda c: lambda v: _compare_versions(v, c)<=0,
    ">":  lambda c: lambda v: _compare_versions(v, c)>0,
    "<":  lambda c: lambda v: _compare_versions(v, c)<0,
}

def _parse_constraints(constraint_str):
    # e.g. ">=1.0.0, <2.0"
    parts = [p.strip() for p in constraint_str.split(",") if p.strip()]
    funcs = []
    for part in parts:
        for op in ("==", ">=", "<=", ">", "<"):
            if part.startswith(op):
                ver = part[len(op):].strip()
                funcs.append(_ops[op](ver))
                break
        else:
            raise ValueError(f"Invalid constraint: {part}")
    return funcs

class DependencySolver:
    def __init__(self, repo_manager):
        self.repo_manager = repo_manager

    def solve(self, constraints):
        """
        constraints: dict pkg_name -> constraint_str
        returns dict pkg_name -> selected_version
        """
        available = self.repo_manager.get_all_packages()
        result = {}
        for pkg, cstr in constraints.items():
            vers = available.get(pkg)
            if not vers:
                raise KeyError(f"Package '{pkg}' not found in any repo")
            funcs = _parse_constraints(cstr)
            # filter
            valid = [v for v in vers if all(f(v) for f in funcs)]
            if not valid:
                raise ValueError(f"No version for '{pkg}' satisfies '{cstr}'")
            # pick max
            valid.sort(key=_parse_version)
            result[pkg] = valid[-1]
        return result
