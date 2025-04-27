import os
import json

class VersionConflictError(Exception):
    pass

def parse_version(vstr):
    # parse semantic version into tuple of ints
    return tuple(int(x) for x in vstr.split("."))

def cmp_version(v1, v2):
    t1 = parse_version(v1)
    t2 = parse_version(v2)
    # compare tuples lexicographically
    return (t1 > t2) - (t1 < t2)

def parse_constraints(spec_str):
    # spec_str like ">=1.0,<3.0" or "==1.0"
    ops = []
    parts = spec_str.split(",")
    for p in parts:
        p = p.strip()
        if p.startswith(">="):
            ops.append((">=", p[2:]))
        elif p.startswith("<="):
            ops.append(("<=", p[2:]))
        elif p.startswith("=="):
            ops.append(("==", p[2:]))
        elif p.startswith(">"):
            ops.append((">", p[1:]))
        elif p.startswith("<"):
            ops.append(("<", p[1:]))
        else:
            # treat as == if no op
            ops.append(("==", p))
    return ops

def satisfies(version, constraints):
    for op, ver in constraints:
        cmp = cmp_version(version, ver)
        if op == ">=" and not (cmp >= 0): return False
        if op == "<=" and not (cmp <= 0): return False
        if op == ">"  and not (cmp > 0): return False
        if op == "<"  and not (cmp < 0): return False
        if op == "==" and not (cmp == 0): return False
    return True

def split_name_spec(spec):
    # split name and version spec
    for op in ["==", ">=", "<=", ">", "<"]:
        if op in spec:
            parts = spec.split(op, 1)
            name = parts[0]
            rest = op + parts[1]
            return name, parse_constraints(rest)
    # no operator: treat as name only
    return spec, []

class PackageManager:
    def __init__(self):
        # v1 state
        self.installed_v1 = set()
        self.deps_v1 = {}         # name -> list of deps
        self.reverse_deps_v1 = {} # name -> set of dependents

        # v2 registry and envs
        self.registry = {}  # name -> { version_str: [dep_specs] }
        self.envs = {}
        self.current_env = None
        # create default env
        self.create_env("base")
        self.use_env("base")

    # ---------------- v1 methods ----------------

    def install_package_v1(self, name, dependencies):
        # detect if already present
        old_deps = self.deps_v1.get(name)
        # tentatively set
        self.deps_v1[name] = list(dependencies)
        # build reverse deps fresh
        # update reverse deps for old deps removal
        # (we'll rebuild reverse_deps_v1 after cycle check)
        if self._has_cycle_v1():
            # revert
            if old_deps is None:
                self.deps_v1.pop(name, None)
            else:
                self.deps_v1[name] = old_deps
            raise Exception("Circular dependency detected")
        # update reverse_deps_v1
        # clear and rebuild full mapping
        self.reverse_deps_v1.clear()
        for pkg, deps in self.deps_v1.items():
            for d in deps:
                self.reverse_deps_v1.setdefault(d, set()).add(pkg)
        # mark installed
        self.installed_v1.add(name)

    def _has_cycle_v1(self):
        visited = set()
        recstack = set()
        def dfs(u):
            visited.add(u)
            recstack.add(u)
            for v in self.deps_v1.get(u, []):
                if v not in visited:
                    if dfs(v):
                        return True
                elif v in recstack:
                    return True
            recstack.remove(u)
            return False
        for node in list(self.deps_v1.keys()):
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def list_packages_v1(self):
        return list(self.installed_v1)

    def is_installed(self, name, version=None):
        if version is None:
            # v1 check
            return name in self.installed_v1
        # v2 check
        env = self.envs.get(self.current_env, {})
        inst = env.get("installed", {})
        return inst.get(name) == version

    def remove_package(self, name):
        # v1 removal
        deps = self.reverse_deps_v1.get(name, set())
        if deps:
            raise Exception(f"Package {name} is a dependency")
        # remove from installed and deps
        self.installed_v1.discard(name)
        mydeps = self.deps_v1.pop(name, [])
        # update reverse_deps_v1
        for d in mydeps:
            if d in self.reverse_deps_v1:
                self.reverse_deps_v1[d].discard(name)
                if not self.reverse_deps_v1[d]:
                    self.reverse_deps_v1.pop(d)
        # also clear reverse_deps_v1 entry for name
        self.reverse_deps_v1.pop(name, None)

    # ---------------- v2 registry/env methods ----------------

    def add_to_registry(self, name, version, dependencies):
        self.registry.setdefault(name, {})
        # store a copy of list
        self.registry[name][version] = list(dependencies)

    def install(self, package_spec):
        name, constraints = split_name_spec(package_spec)
        # top-level call: parent=None means direct install
        self._install_recursive(name, constraints, parent=None)

    def _install_recursive(self, name, constraints, parent):
        # check registry
        if name not in self.registry:
            raise Exception(f"Package {name} not in registry")
        # select a version
        candidates = []
        for ver in self.registry[name].keys():
            if not constraints or satisfies(ver, constraints):
                candidates.append(ver)
        if not candidates:
            raise VersionConflictError(f"No version for {name} matches {constraints}")
        # pick latest
        candidates.sort(key=lambda v: parse_version(v))
        chosen = candidates[-1]
        # check conflict with installed
        inst = self.envs[self.current_env]["installed"]
        if name in inst:
            if inst[name] != chosen:
                raise VersionConflictError(f"Conflict on {name}: installed {inst[name]}, required {chosen}")
            # already installed needed version: record reason if missing
        else:
            # install it
            inst[name] = chosen
            reasons = self.envs[self.current_env]["reasons"]
            if parent is None:
                reasons[name] = "direct install"
            else:
                reasons[name] = f"dependency of {parent[0]}=={parent[1]}"
        # install dependencies
        deps = self.registry[name][chosen]
        for dep_spec in deps:
            dep_name, dep_constraints = split_name_spec(dep_spec)
            self._install_recursive(dep_name, dep_constraints, parent=(name, chosen))

    def install_package(self, name, version, dependencies):
        # direct install without registry solver: register then install
        # add to registry
        self.add_to_registry(name, version, dependencies)
        # install this exact version ignoring dependencies
        inst = self.envs[self.current_env]["installed"]
        if name not in inst:
            inst[name] = version
            self.envs[self.current_env]["reasons"][name] = "direct install"
        # do not auto-install deps here

    def create_env(self, env_name):
        # create a new environment
        if env_name in self.envs:
            # already exists: do nothing
            return
        # make directory for env isolation
        try:
            os.makedirs(env_name, exist_ok=True)
        except:
            pass
        self.envs[env_name] = {"installed": {}, "reasons": {}}

    def use_env(self, env_name):
        if env_name not in self.envs:
            raise Exception(f"No such environment {env_name}")
        self.current_env = env_name

    def generate_lockfile(self, env_name):
        # write installed packages of env_name to lock.json
        if env_name not in self.envs:
            raise Exception(f"No such environment {env_name}")
        data = self.envs[env_name]["installed"]
        path = "lock.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    def install_from_lockfile(self, lockfile_path):
        with open(lockfile_path) as f:
            data = json.load(f)
        # clear current env
        inst = self.envs[self.current_env]["installed"]
        reasons = self.envs[self.current_env]["reasons"]
        inst.clear()
        reasons.clear()
        # install all from lockfile
        for name, version in data.items():
            inst[name] = version
            reasons[name] = "from lockfile"

    def find_package(self, name, version_spec):
        if name not in self.registry:
            return []
        constraints = parse_constraints(version_spec)
        res = []
        for ver in self.registry[name].keys():
            if satisfies(ver, constraints):
                res.append((name, ver))
        return res

    def why(self, name):
        # find in current env reasons
        reasons = self.envs[self.current_env]["reasons"]
        # find matching name; pick reason
        if name not in reasons:
            return None
        return reasons[name]
