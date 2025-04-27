import os
import json
import re

class VersionConflictError(Exception):
    pass

class PackageManager:
    def __init__(self):
        # V1 data
        self.installed_v1 = set()
        self.deps_v1 = {}       # name -> list of deps
        self.rev_deps_v1 = {}   # name -> set of parents

        # V2 data
        self.registry = {}      # name -> {version: [dep_specs]}
        # environments: name -> env_data
        # env_data: {
        #   'direct': {name: set(versions)},
        #   'solver': {name: version},
        #   'reasons': {name: reason_str}
        # }
        self.envs = {}
        self.current_env = 'default'
        self.envs[self.current_env] = self._make_env()

    # ------ V1 methods ------

    def install_package_v1(self, name, dependencies):
        # If already installed, do nothing
        if name in self.installed_v1:
            return
        # Record dependencies
        self.deps_v1[name] = list(dependencies)
        # Ensure reverse deps entry exists
        if name not in self.rev_deps_v1:
            self.rev_deps_v1[name] = set()
        # Update reverse deps
        for dep in dependencies:
            if dep not in self.rev_deps_v1:
                self.rev_deps_v1[dep] = set()
            self.rev_deps_v1[dep].add(name)
        # Detect cycles
        if self._detect_cycle_v1():
            # rollback
            for dep in dependencies:
                self.rev_deps_v1[dep].discard(name)
            del self.deps_v1[name]
            raise Exception("Circular dependency detected")
        # Mark installed
        self.installed_v1.add(name)

    def _detect_cycle_v1(self):
        def dfs(node, path):
            if node in path:
                return True
            path.add(node)
            for ch in self.deps_v1.get(node, []):
                if dfs(ch, path):
                    return True
            path.remove(node)
            return False
        for pkg in self.deps_v1:
            if dfs(pkg, set()):
                return True
        return False

    def remove_package(self, name):
        if name not in self.installed_v1:
            return
        # Can't remove if someone depends on it
        parents = self.rev_deps_v1.get(name, set())
        if parents:
            raise Exception(f"{name} is a dependency")
        # Remove
        self.installed_v1.remove(name)
        deps = self.deps_v1.get(name, [])
        # Cleanup reverse deps
        for dep in deps:
            if dep in self.rev_deps_v1:
                self.rev_deps_v1[dep].discard(name)
        # Cleanup maps
        if name in self.deps_v1:
            del self.deps_v1[name]
        if name in self.rev_deps_v1:
            del self.rev_deps_v1[name]

    def is_installed_v1(self, name):
        return name in self.installed_v1

    def list_packages_v1(self):
        return list(self.installed_v1)

    # ------ V2 methods ------

    def add_to_registry(self, name, version, dependencies):
        """Register a package version with its dependency specs."""
        if name not in self.registry:
            self.registry[name] = {}
        self.registry[name][version] = list(dependencies)

    def install_package(self, name, version, dependencies):
        """
        Directly add a package version to registry and mark it installed (no solver).
        """
        self.add_to_registry(name, version, dependencies)
        env = self.envs[self.current_env]
        env['direct'].setdefault(name, set()).add(version)

    def parse_spec(self, spec_str):
        """
        Parse a spec like "A>=1.0,<3.0" or "B==1.0" into (name, [(op,ver),...])
        """
        parts = spec_str.split(',')
        # first part has name
        m = re.match(r"^([A-Za-z0-9_]+)(==|>=|<=|>|<)(.+)$", parts[0])
        if not m:
            raise Exception(f"Invalid spec '{spec_str}'")
        name = m.group(1)
        constraints = [(m.group(2), m.group(3))]
        # remaining parts
        for p in parts[1:]:
            m2 = re.match(r"^(==|>=|<=|>|<)(.+)$", p)
            if not m2:
                raise Exception(f"Invalid constraint '{p}' in '{spec_str}'")
            constraints.append((m2.group(1), m2.group(2)))
        return name, constraints

    def parse_constraints(self, spec_str):
        """
        Parse only constraints part like ">=1.5,<2.0" into list of (op,ver).
        """
        constraints = []
        parts = spec_str.split(',')
        for p in parts:
            m = re.match(r"^(==|>=|<=|>|<)(.+)$", p)
            if not m:
                raise Exception(f"Invalid constraint '{p}'")
            constraints.append((m.group(1), m.group(2)))
        return constraints

    def parse_version(self, version):
        """Convert 'x.y.z' into a tuple of ints."""
        return tuple(int(x) for x in version.split('.'))

    def match_constraints(self, version, constraints):
        ver_tup = self.parse_version(version)
        for op, vstr in constraints:
            target = self.parse_version(vstr)
            if op == '==':
                if ver_tup != target:
                    return False
            elif op == '>=':
                if ver_tup < target:
                    return False
            elif op == '<=':
                if ver_tup > target:
                    return False
            elif op == '>':
                if ver_tup <= target:
                    return False
            elif op == '<':
                if ver_tup >= target:
                    return False
        return True

    def install(self, spec_str, parent=None):
        """
        Resolver-based install. Handles dependency constraints, picks latest compatible
        version, and tracks reasons.
        """
        name, constraints = self.parse_spec(spec_str)
        env = self.envs[self.current_env]
        # Already solved?
        if name in env['solver']:
            inst_v = env['solver'][name]
            if self.match_constraints(inst_v, constraints):
                return
            else:
                raise VersionConflictError(f"Version conflict for {name}")
        # Check direct-installed
        if name in env['direct']:
            for dv in env['direct'][name]:
                if self.match_constraints(dv, constraints):
                    return
        # Pick from registry
        versions = list(self.registry.get(name, {}).keys())
        candidates = [v for v in versions if self.match_constraints(v, constraints)]
        if not candidates:
            raise Exception(f"No matching version for {name}")
        # pick latest
        selected = sorted(candidates, key=self.parse_version, reverse=True)[0]
        # install dependencies first
        for dep_spec in self.registry[name][selected]:
            self.install(dep_spec, parent=(name, selected))
        # now install this package
        env['solver'][name] = selected
        if parent is None:
            env['reasons'][name] = "direct install"
        else:
            p_name, p_ver = parent
            env['reasons'][name] = f"dependency of {p_name}=={p_ver}"

    def create_env(self, env_name):
        if env_name in self.envs:
            return
        os.mkdir(env_name)
        self.envs[env_name] = self._make_env()

    def use_env(self, env_name):
        if env_name not in self.envs:
            raise Exception(f"Environment '{env_name}' does not exist")
        self.current_env = env_name

    def generate_lockfile(self, env_name):
        if env_name not in self.envs:
            raise Exception(f"No such environment '{env_name}'")
        env = self.envs[env_name]
        lock = {}
        # include solver-installed
        for n, v in env['solver'].items():
            lock[n] = v
        # include direct-installed
        for n, vers in env['direct'].items():
            # if both solver and direct for same name, solver takes precedence
            for v in vers:
                if n not in lock:
                    lock[n] = v
        path = "lock.json"
        with open(path, "w") as f:
            json.dump(lock, f)
        return path

    def install_from_lockfile(self, lockfile_path):
        with open(lockfile_path) as f:
            data = json.load(f)
        # install in current env
        for name, version in data.items():
            self.install(f"{name}=={version}")

    def find_package(self, name, version_spec):
        if name not in self.registry:
            return []
        constraints = self.parse_constraints(version_spec)
        results = []
        for v in self.registry[name]:
            if self.match_constraints(v, constraints):
                results.append((name, v))
        return results

    def why(self, name):
        env = self.envs[self.current_env]
        if name in env['solver']:
            return env['reasons'].get(name)
        if name in env['direct']:
            return "direct install"
        return None

    # ------ alias for v1 is_installed ------
    def is_installed(self, name, version=None):
        # v1 usage when version is None and direct v2 not in play
        if version is None:
            return self.is_installed_v1(name)
        # v2 check
        env = self.envs[self.current_env]
        if name in env['solver'] and env['solver'][name] == version:
            return True
        if name in env['direct'] and version in env['direct'][name]:
            return True
        return False

    def _make_env(self):
        return {
            'direct': {},   # name -> set of versions
            'solver': {},   # name -> single version
            'reasons': {}   # name -> reason string
        }
