from utils import parse_version, parse_constraints

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
            funcs = parse_constraints(cstr)
            valid = [v for v in vers if all(f(v) for f in funcs)]
            if not valid:
                raise ValueError(f"No version for '{pkg}' satisfies '{cstr}'")
            valid.sort(key=parse_version)
            result[pkg] = valid[-1]
        return result
