import os
import json
import shutil

class VersionConflictError(Exception):
    pass

def _version_to_tuple(v):
    # Convert "1.2.3" -> (1,2,3)
    return tuple(int(x) for x in v.split('.'))

class EnvData:
    def __init__(self):
        # V1 data
        self.dep_graph_v1 = {}     # name -> set of deps
        self.rev_deps_v1 = {}      # name -> set of dependents
        self.installed_v1 = set()
        # V2 data
        self.installed_v2 = {}     # name -> version
        self.reasons = {}          # name -> reason string

class PackageManager:
    def __init__(self):
        # Registry for v2: name -> { version: [dep_specs] }
        self.registry = {}
        # Environments
        self.envs = {}
        # Default (global) environment
        self.envs["global"] = EnvData()
        self.current_env = "global"

    # ---------- V1 methods ----------
    def install_package_v1(self, name, dependencies):
        env = self.envs[self.current_env]
        g = env.dep_graph_v1
        r = env.rev_deps_v1
        # Prepare old/new deps
        new_deps = set(dependencies)
        old_deps = g.get(name, set())
        # Update graph
        g[name] = new_deps.copy()
        # Ensure reverse deps entries
        r.setdefault(name, set())
        # Remove old reverse links
        for dep in (old_deps - new_deps):
            if dep in r:
                r[dep].discard(name)
        # Add new reverse links
        for dep in (new_deps - old_deps):
            r.setdefault(dep, set()).add(name)
        # Recursive install with cycle detection
        visited = set()
        stack = set()
        def dfs(pkg):
            if pkg in stack:
                raise Exception("Circular dependency detected")
            stack.add(pkg)
            # Ensure graph entry exists
            g.setdefault(pkg, set())
            r.setdefault(pkg, set())
            # Mark installed
            env.installed_v1.add(pkg)
            # Recurse
            for d in g[pkg]:
                dfs(d)
            stack.remove(pkg)
        dfs(name)

    def remove_package(self, name):
        env = self.envs[self.current_env]
        g = env.dep_graph_v1
        r = env.rev_deps_v1
        if name not in env.installed_v1:
            return
        if r.get(name):
            if len(r[name]) > 0:
                raise Exception(f"Package {name} is a dependency")
        # Remove edges
        deps = g.get(name, set()).copy()
        for dep in deps:
            if dep in r:
                r[dep].discard(name)
        # Remove entries
        env.installed_v1.discard(name)
        g.pop(name, None)
        r.pop(name, None)

        # Also clean up any reverse references to this name
        for pkg, depset in g.items():
            if name in depset:
                depset.discard(name)
        for pkg, revs in r.items():
            if name in revs:
                revs.discard(name)

    def list_packages_v1(self):
        env = self.envs[self.current_env]
        return list(env.installed_v1)

    def is_installed(self, name, version=None):
        env = self.envs[self.current_env]
        if version is None:
            # V1 check
            return name in env.installed_v1
        # V2 check
        return env.installed_v2.get(name) == version

    # ---------- V2 registry and install ----------
    def add_to_registry(self, name, version, dependencies):
        self.registry.setdefault(name, {})[version] = list(dependencies)

    def install_package(self, name, version, dependencies):
        """
        For v2: convenience to register and install a specific version.
        """
        self.add_to_registry(name, version, dependencies)
        # Direct install
        spec = f"{name}=={version}"
        self.install(spec)

    def install(self, spec):
        """
        Install package by specification, e.g. "A>=1.0,<3.0" or "B==1.0"
        """
        # Resolve recursively, keeping state
        env = self.envs[self.current_env]
        # Start resolution
        self._resolve(spec, parent=None, env=env)

    def _resolve(self, spec, parent, env):
        name, constraints = self._parse_spec(spec)
        # Choose version
        chosen = self._choose_version(name, constraints)
        # Check existing
        if name in env.installed_v2:
            if env.installed_v2[name] != chosen:
                raise VersionConflictError(
                    f"Conflict on {name}: {env.installed_v2[name]} vs {chosen}"
                )
            # Already installed same version: skip deps
            return
        # Install it
        env.installed_v2[name] = chosen
        # Record reason
        if parent is None:
            env.reasons[name] = "direct install"
        else:
            env.reasons[name] = f"dependency of {parent}"
        # Recurse into its dependencies
        deps = self.registry.get(name, {}).get(chosen, [])
        for dspec in deps:
            # parent for child is name==chosen
            self._resolve(dspec, f"{name}=={chosen}", env)

    def _parse_spec(self, spec):
        spec = spec.strip()
        idx = None
        for i, ch in enumerate(spec):
            if ch in "=<>":
                idx = i
                break
        if idx is None:
            # No constraint => any version
            return spec, []
        name = spec[:idx]
        rest = spec[idx:]
        # Multiple constraints comma-separated
        parts = rest.split(',')
        return name, [p.strip() for p in parts if p.strip()]

    def _choose_version(self, name, constraints):
        if name not in self.registry:
            raise VersionConflictError(f"No such package in registry: {name}")
        versions = list(self.registry[name].keys())
        # Filter by constraints
        ok = []
        for v in versions:
            if self._match_all(v, constraints):
                ok.append(v)
        if not ok:
            raise VersionConflictError(f"No versions match for {name}{constraints}")
        # Pick latest by version tuple
        ok.sort(key=_version_to_tuple)
        return ok[-1]

    def _match_all(self, version, constraints):
        vt = _version_to_tuple(version)
        for c in constraints:
            op = None
            ver = None
            # Determine operator
            for candidate in ("==", ">=", "<=", ">", "<"):
                if c.startswith(candidate):
                    op = candidate
                    ver = c[len(candidate):]
                    break
            if op is None:
                continue
            vt2 = _version_to_tuple(ver)
            if op == "==":
                if not (vt == vt2): return False
            elif op == ">=":
                if not (vt >= vt2): return False
            elif op == "<=":
                if not (vt <= vt2): return False
            elif op == ">":
                if not (vt > vt2): return False
            elif op == "<":
                if not (vt < vt2): return False
        return True

    # ---------- Environments ----------
    def create_env(self, env_name):
        if env_name in self.envs:
            raise Exception(f"Environment {env_name} already exists")
        # Create directory
        os.makedirs(env_name, exist_ok=True)
        # Initialize env data
        self.envs[env_name] = EnvData()

    def use_env(self, env_name):
        if env_name not in self.envs:
            raise Exception(f"No such environment: {env_name}")
        self.current_env = env_name

    # ---------- Lockfile ----------
    def generate_lockfile(self, env_name):
        if env_name not in self.envs:
            raise Exception(f"No such environment: {env_name}")
        env = self.envs[env_name]
        data = {}
        for name, ver in env.installed_v2.items():
            data[name] = ver
        # Write to env directory
        lock_path = os.path.join(env_name, "lock.json")
        with open(lock_path, "w") as f:
            json.dump(data, f, indent=2)
        return lock_path

    def install_from_lockfile(self, lockfile_path):
        # Read lockfile
        with open(lockfile_path) as f:
            data = json.load(f)
        # Install each entry
        for name, ver in data.items():
            spec = f"{name}=={ver}"
            self.install(spec)

    # ---------- Search / Query ----------
    def find_package(self, name, version_spec):
        name = name.strip()
        # Parse constraints on version only
        # We simulate spec for version: e.g. ">=1.5"
        # reuse _parse_spec by prefixing name
        fake_spec = name + version_spec
        _, constraints = self._parse_spec(fake_spec)
        results = []
        for v in self.registry.get(name, {}):
            if self._match_all(v, constraints):
                results.append((name, v))
        return results

    def why(self, name):
        env = self.envs[self.current_env]
        return env.reasons.get(name)
