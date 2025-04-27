import os
import json

class VersionConflictError(Exception):
    pass

class PackageManager:
    def __init__(self):
        # V1 data
        self.installed_v1 = set()
        self.deps_v1 = {}  # name -> set(deps)

        # V2 data
        # registry: name -> version -> list of dependency strings
        self.registry = {}
        # environments: env_name -> {'installed': {name: [versions...]},
        #                           'reasons': {(name,ver): reason}}
        self.envs = {}
        self.current_env = None

    #
    # ===== V1 Methods =====
    #
    def install_package_v1(self, name, dependencies):
        # Update dependency mapping
        self.deps_v1[name] = set(dependencies)
        # Recursively install
        visited = set()
        def dfs(pkg):
            if pkg in visited:
                raise Exception(f"Circular dependency detected: {pkg}")
            visited.add(pkg)
            # If we have declared deps for pkg, use them; otherwise empty
            for dep in self.deps_v1.get(pkg, []):
                dfs(dep)
            self.installed_v1.add(pkg)
            visited.remove(pkg)

        dfs(name)

    def remove_package(self, name):
        # Only allowed if no other installed package depends on it
        for pkg in self.installed_v1:
            if pkg == name:
                continue
            if name in self.deps_v1.get(pkg, []):
                raise Exception(f"Package {name} is a dependency of {pkg}")
        # Safe to remove
        if name in self.installed_v1:
            self.installed_v1.remove(name)
        # Optionally remove deps_v1 entry
        if name in self.deps_v1:
            del self.deps_v1[name]

    def list_packages_v1(self):
        return list(self.installed_v1)

    def is_installed_v1(self, name):
        return name in self.installed_v1

    #
    # ===== V2 Helpers =====
    #
    def _parse_constraint_str(self, s):
        """Parse a constraint string like 'A>=1.0,<3.0' or '>=1.5'."""
        # find first operator char
        i = 0
        while i < len(s) and s[i] not in "=<>":
            i += 1
        name = s[:i] if i>0 else None
        rest = s[i:]
        parts = rest.split(',') if rest else []
        cons = []
        for part in parts:
            part = part.strip()
            op = None
            ver = None
            if part.startswith("=="):
                op = "=="; ver = part[2:]
            elif part.startswith(">="):
                op = ">="; ver = part[2:]
            elif part.startswith("<="):
                op = "<="; ver = part[2:]
            elif part.startswith(">"):
                op = ">"; ver = part[1:]
            elif part.startswith("<"):
                op = "<"; ver = part[1:]
            else:
                continue
            cons.append((op, ver))
        return name, cons

    def _ver_to_tuple(self, v):
        return tuple(int(x) for x in v.split('.'))

    def _check_version(self, ver, constraints):
        vt = self._ver_to_tuple(ver)
        for op, v in constraints:
            vt2 = self._ver_to_tuple(v)
            if op == "==" and not (vt == vt2):
                return False
            if op == ">=" and not (vt >= vt2):
                return False
            if op == "<=" and not (vt <= vt2):
                return False
            if op == ">" and not (vt > vt2):
                return False
            if op == "<" and not (vt < vt2):
                return False
        return True

    #
    # ===== Registry =====
    #
    def add_to_registry(self, name, version, dependencies):
        self.registry.setdefault(name, {})[version] = list(dependencies)

    #
    # ===== Environment Management =====
    #
    def create_env(self, env_name):
        # Create dir
        try:
            os.makedirs(env_name, exist_ok=True)
        except Exception:
            pass
        # Init env data
        self.envs[env_name] = {
            'installed': {},  # name -> list of versions
            'reasons': {}     # (name,ver) -> reason string
        }

    def use_env(self, env_name):
        if env_name not in self.envs:
            raise Exception(f"Environment {env_name} does not exist")
        self.current_env = env_name

    def _get_current_env(self):
        if self.current_env is None:
            return None
        return self.envs[self.current_env]

    #
    # ===== V2 Install / Remove =====
    #
    def install_package(self, name, version, dependencies):
        # Add to registry
        self.add_to_registry(name, version, dependencies)
        # Install exactly this version
        req = f"{name}=={version}"
        self.install(req)

    def install(self, requirement):
        """Install using dependency solver, requirement like 'A>=1.0,<3.0' or 'B==1.0'."""
        env = self._get_current_env()
        if env is None:
            # no env: nothing to do
            raise Exception("No environment selected")
        # Parse top-level requirement
        pkg_name, constraints = self._parse_constraint_str(requirement)
        if pkg_name not in self.registry:
            raise Exception(f"Package {pkg_name} not in registry")
        # Session tracking
        session = {
            'chosen': {},   # name -> version
        }
        def resolve(req_str, parent):
            name, cons = self._parse_constraint_str(req_str)
            if name not in self.registry:
                raise Exception(f"Package {name} not in registry")
            # find candidate versions
            candidates = []
            for v in self.registry[name]:
                if self._check_version(v, cons):
                    candidates.append(v)
            if not candidates:
                raise Exception(f"No version of {name} matches {cons}")
            # select latest
            candidates.sort(key=self._ver_to_tuple)
            ver = candidates[-1]
            # conflict with session
            if name in session['chosen'] and session['chosen'][name] != ver:
                raise VersionConflictError(f"Version conflict on {name}")
            # conflict with env
            if name in env['installed']:
                if ver not in env['installed'][name]:
                    raise VersionConflictError(f"Version conflict on {name}")
            # record choice
            if name not in session['chosen']:
                session['chosen'][name] = ver
                # record reason
                key = (name, ver)
                if parent is None:
                    env['reasons'][key] = "direct install"
                else:
                    p_name, p_ver = parent
                    env['reasons'][key] = f"dependency of {p_name}=={p_ver}"
                # resolve dependencies of this package
                deps = self.registry[name][ver]
                for dep in deps:
                    resolve(dep, (name, ver))

        # begin resolution
        resolve(requirement, None)
        # perform install of chosen that are not installed
        for name, ver in session['chosen'].items():
            if ver in env['installed'].get(name, []):
                continue
            env['installed'].setdefault(name, []).append(ver)
        # done

    def is_installed(self, name, version=None):
        # V2 if version given or env selected
        env = self._get_current_env()
        if version is None and env is None:
            return self.is_installed_v1(name)
        if env is None:
            return False
        if version is None:
            # no version specified: any version?
            return name in env['installed'] and bool(env['installed'][name])
        return name in env['installed'] and version in env['installed'][name]

    #
    # ===== Lockfile =====
    #
    def generate_lockfile(self, env_name):
        if env_name not in self.envs:
            raise Exception(f"No such environment {env_name}")
        data = self.envs[env_name]['installed']
        # determine filename: prefix before first underscore
        prefix = env_name.split('_')[0]
        fname = f"{prefix}.lock.json"
        to_write = {}
        for name, vers in data.items():
            # pick single version if one, else latest
            if not vers:
                continue
            vers_sorted = sorted(vers, key=self._ver_to_tuple)
            to_write[name] = vers_sorted[-1]
        with open(fname, 'w') as f:
            json.dump(to_write, f)
        return fname

    def install_from_lockfile(self, lockfile_path):
        env = self._get_current_env()
        if env is None:
            raise Exception("No environment selected")
        with open(lockfile_path) as f:
            mapping = json.load(f)
        # Install each exactly
        for name, ver in mapping.items():
            req = f"{name}=={ver}"
            self.install(req)

    #
    # ===== Query =====
    #
    def find_package(self, name, version_spec):
        if name not in self.registry:
            return []
        # parse version_spec as constraints only
        _, cons = self._parse_constraint_str(version_spec)
        results = []
        for v in self.registry[name]:
            if self._check_version(v, cons):
                results.append((name, v))
        return results

    def why(self, name):
        env = self._get_current_env()
        if env is None:
            raise Exception("No environment selected")
        if name not in env['installed']:
            return None
        # pick one version
        ver = env['installed'][name][0]
        reason = env['reasons'].get((name, ver))
        return reason
